#!/usr/bin/env python3
"""Generate R247 successor shop drawings, RFQ payload, and unpowered arm assembly definition."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENT = "HR-V0-MECH-SHOP-RFQ-ASSY-P0.1"
DRAW_IDENT = "HR-V0-MECH-SHOP-DWG-P0.2"
ARCH = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
BIND_IDENT = "HR-V0-MECH-BOM-BIND-P0.3"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.11"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OLD_WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
BINDING = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.3.csv"
SRC = ROOT / "cad/hr-v0/generated/mechanical-shop-drawing-p0.2"
REL = ROOT / "release/hr-v0/mechanical-shop-rfq-assembly-p0.1"
CFG_OLD = ROOT / "configuration/hr-v0-config-reconciliation-p0.10"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.11"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.11"
GENERATED_ROOT = ROOT / "cad/hr-v0/generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated_digest(path: Path) -> str:
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(data).hexdigest().upper()
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_generated_source_manifest() -> None:
    records = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            records.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_digest(path),
                "revision": MECHANICAL_REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, ["file", "sha256", "revision", "status"], records)


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    write_csv(directory / "file-manifest.csv", ["path","bytes","sha256"], records)


def geometry_fingerprint(text: str) -> str:
    tags = re.findall(r"<(?:line|circle|polyline|rect)\b[^>]*class=\"(?:profile|hole|csk|center|dim|ext|recess)\"[^>]*/?>", text)
    canonical = "\n".join(re.sub(r"\s+", " ", tag.strip()) for tag in tags)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def successor_drawing(part: dict[str, str], source: Path, destination: Path) -> tuple[str, str]:
    text = source.read_text(encoding="utf-8")
    old_height_match = re.search(r"<svg[^>]*height=\"(\d+)\"[^>]*viewBox=\"0 0 1600 (\d+)\"", text)
    if not old_height_match or old_height_match.group(1) != old_height_match.group(2):
        raise SystemExit(f"unexpected drawing root: {source}")
    old_height = int(old_height_match.group(1)); new_height = old_height + 370
    text = text.replace(f'height="{old_height}" viewBox="0 0 1600 {old_height}"', f'height="{new_height}" viewBox="0 0 1600 {new_height}"', 1)
    text = text.replace(OLD_WARNING, WARNING)
    text = text.replace("HR-V0-MECH-DWG-P0.1", DRAW_IDENT)
    text = text.replace("HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE", ARCH)
    text = text.replace("STATUS: NONSELECTED CANDIDATE / FAI UNEXECUTED", "STATUS: INTEGRATED HELD SHOP CANDIDATE / FAI UNEXECUTED")
    drawing_no = f"HRV0-{part['part_id']}-SD-P0.2"
    block_y = old_height + 20
    _superseded_three_column_block = f'''<rect class="shopblock" x="20" y="{block_y}" width="1560" height="215" fill="#f7fbfe" stroke="#082f5b" stroke-width="3"/>
<line class="shopblock" x1="20" y1="{block_y+58}" x2="1580" y2="{block_y+58}" stroke="#082f5b"/><line class="shopblock" x1="20" y1="{block_y+116}" x2="1580" y2="{block_y+116}" stroke="#082f5b"/>
<line class="shopblock" x1="620" y1="{block_y}" x2="620" y2="{block_y+215}" stroke="#082f5b"/><line class="shopblock" x1="1110" y1="{block_y}" x2="1110" y2="{block_y+215}" stroke="#082f5b"/>
<text x="40" y="{block_y+26}" class="tablehead">DRAWING NUMBER</text><text x="220" y="{block_y+26}" class="tabletxt">{drawing_no}</text>
<text x="640" y="{block_y+26}" class="tablehead">REVISION / STATE</text><text x="820" y="{block_y+26}" class="tabletxt">P0.2 · INTEGRATED HELD CANDIDATE</text>
<text x="1130" y="{block_y+26}" class="tablehead">UNITS / SCALE / SHEET</text><text x="1360" y="{block_y+26}" class="tabletxt">mm · NTS · 1 OF 1</text>
<text x="40" y="{block_y+84}" class="tablehead">MATERIAL / FINISH</text><text x="220" y="{block_y+84}" class="tabletxt">6061-T651 CANDIDATE · BARE AS-MACHINED</text>
<text x="640" y="{block_y+84}" class="tablehead">SOURCE BINDING</text><text x="820" y="{block_y+84}" class="tabletxt">{BIND_IDENT} · {ARCH}</text>
<text x="1130" y="{block_y+84}" class="tablehead">GEOMETRY CHANGE</text><text x="1360" y="{block_y+84}" class="tabletxt">NONE FROM P0.1</text>
<text x="40" y="{block_y+142}" class="tablehead">INSPECTION REGISTRATION</text><text x="270" y="{block_y+142}" class="tabletxt">ICF-01 CMM METHOD RETAINED</text>
<text x="640" y="{block_y+142}" class="tablehead">FORMAL DATUM / GD&amp;T</text><text x="850" y="{block_y+142}" class="tabletxt">SELECTION REQUIRED · QUALIFIED DISPOSITION OPEN</text>
<text x="1130" y="{block_y+142}" class="tablehead">FABRICATION AUTHORITY</text><text x="1360" y="{block_y+142}" class="tabletxt">FALSE</text>
<text x="40" y="{block_y+190}" class="tablehead">THIS SUCCESSOR CORRECTS IDENTIFIER, WARNING, REVISION AND TITLE-BLOCK CONTROL ONLY. STEP/DXF GEOMETRY IS UNCHANGED.</text>'''
    block = f'''<rect class="shopblock" x="20" y="{block_y}" width="1560" height="330" fill="#f7fbfe" stroke="#082f5b" stroke-width="3"/>
<line class="shopblock" x1="20" y1="{block_y+54}" x2="1580" y2="{block_y+54}" stroke="#082f5b"/><line class="shopblock" x1="20" y1="{block_y+108}" x2="1580" y2="{block_y+108}" stroke="#082f5b"/>
<line class="shopblock" x1="20" y1="{block_y+180}" x2="1580" y2="{block_y+180}" stroke="#082f5b"/><line class="shopblock" x1="20" y1="{block_y+234}" x2="1580" y2="{block_y+234}" stroke="#082f5b"/>
<line class="shopblock" x1="20" y1="{block_y+288}" x2="1580" y2="{block_y+288}" stroke="#082f5b"/>
<line class="shopblock" x1="620" y1="{block_y}" x2="620" y2="{block_y+54}" stroke="#082f5b"/><line class="shopblock" x1="1110" y1="{block_y}" x2="1110" y2="{block_y+54}" stroke="#082f5b"/>
<line class="shopblock" x1="800" y1="{block_y+54}" x2="800" y2="{block_y+108}" stroke="#082f5b"/><line class="shopblock" x1="800" y1="{block_y+180}" x2="800" y2="{block_y+288}" stroke="#082f5b"/>
<text x="40" y="{block_y+26}" class="tablehead">DRAWING NUMBER</text><text x="220" y="{block_y+26}" class="tabletxt">{drawing_no}</text>
<text x="640" y="{block_y+26}" class="tablehead">REVISION / STATE</text><text x="790" y="{block_y+26}" class="tabletxt">P0.2 · INTEGRATED HELD CANDIDATE</text>
<text x="1130" y="{block_y+26}" class="tablehead">UNITS / SCALE / SHEET</text><text x="1360" y="{block_y+26}" class="tabletxt">mm · NTS · 1 OF 1</text>
<text x="40" y="{block_y+80}" class="tablehead">MATERIAL / FINISH</text><text x="220" y="{block_y+80}" class="tabletxt">6061-T651 CANDIDATE · BARE AS-MACHINED</text>
<text x="820" y="{block_y+80}" class="tablehead">GEOMETRY CHANGE</text><text x="1040" y="{block_y+80}" class="tabletxt">NONE FROM P0.1</text>
<text x="40" y="{block_y+134}" class="tablehead">SOURCE BINDING</text><text x="220" y="{block_y+134}" class="tabletxt" data-shop-field="source-binding">{BIND_IDENT}</text>
<text x="40" y="{block_y+162}" class="tablehead">ARCHITECTURE</text><text x="220" y="{block_y+162}" class="tabletxt" data-shop-field="architecture">{ARCH}</text>
<text x="40" y="{block_y+206}" class="tablehead">INSPECTION REGISTRATION</text><text x="270" y="{block_y+206}" class="tabletxt">ICF-01 CMM METHOD RETAINED</text>
<text x="820" y="{block_y+206}" class="tablehead">FORMAL DATUM / GD&amp;T</text><text x="1040" y="{block_y+206}" class="tabletxt">SELECTION REQUIRED · QUALIFIED DISPOSITION OPEN</text>
<text x="40" y="{block_y+260}" class="tablehead">FABRICATION AUTHORITY</text><text x="270" y="{block_y+260}" class="tabletxt">FALSE</text>
<text x="820" y="{block_y+260}" class="tablehead">PHYSICAL / QUALIFIED EVIDENCE</text><text x="1120" y="{block_y+260}" class="tabletxt">NOT EXECUTED</text>
<text x="40" y="{block_y+314}" class="tablehead">THIS SUCCESSOR CORRECTS IDENTIFIER, WARNING, REVISION AND TITLE-BLOCK CONTROL ONLY. STEP/DXF GEOMETRY IS UNCHANGED.</text>'''
    text = text.replace("</svg>", block + "</svg>")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")
    return geometry_fingerprint(source.read_text(encoding="utf-8")), geometry_fingerprint(text)


def make_page(title: str, intro: str, directory: Path, csv_names: list[str]) -> str:
    sections = []
    for name in csv_names:
        rows, fields = read_csv(directory / name)
        head = "".join(f"<th>{html.escape(field.replace('_',' '))}</th>" for field in fields)
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[field]))}</td>" for field in fields) + "</tr>" for row in rows)
        sections.append(f"<section><h2>{html.escape(name[:-4].replace('-',' ').title())}</h2><p><a class='download' href='{html.escape(name)}'>Download {html.escape(name)}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>")
    drawing_links = "".join(f"<a class='drawing' href='{html.escape(p.name)}'>{html.escape(p.name)}</a>" for p in sorted(directory.glob("MV0-*_shop-drawing_P0.2.svg")))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>
:root{{--ink:#082a4a;--blue:#075ea8;--sky:#dff3ff;--gold:#f3bd28;--paper:#f8fbfd;--line:#9bc6e4;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}.warning{{font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd;border:3px solid var(--gold);padding:14px;border-radius:12px}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.5em 0 .2em}}h2{{font-size:clamp(24px,2.6vw,36px);margin-top:1.7em}}.status{{font-size:18px;font-weight:800;color:var(--danger)}}.drawings{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.drawing{{display:block;background:white;border:2px solid var(--line);border-radius:12px;padding:18px;color:var(--blue);font-size:16px;font-weight:700;overflow-wrap:anywhere}}.download{{font-size:16px;font-weight:700;color:var(--blue)}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{position:sticky;top:0;background:var(--sky);font-size:14px}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:34px}}}}
</style></head><body><header><div><p class='warning'>{html.escape(WARNING)}</p><h1>{html.escape(title)}</h1><p>{html.escape(intro)}</p></div></header><main><p class='status'>REVIEW/RFQ PREPARATION ONLY · NO PROVIDER CONTACT OR PHYSICAL WORK AUTHORIZED</p><h2>Successor shop drawings</h2><div class='drawings'>{drawing_links}</div>{''.join(sections)}</main></body></html>"""


def generate_package() -> None:
    for directory in (SRC, REL):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    bindings, _ = read_csv(BINDING)
    if len(bindings) != 5 or any(row["architecture_id"] != ARCH for row in bindings): raise SystemExit("current P0.3 binding required")
    source_rows = []
    title_rows = []
    payload_rows = []
    for index, part in enumerate(bindings, 1):
        old_drawing = ROOT / part["drawing_path"]
        new_name = f"{part['part_id']}_shop-drawing_P0.2.svg"
        new_drawing = SRC / new_name
        old_fp, new_fp = successor_drawing(part, old_drawing, new_drawing)
        if old_fp != new_fp: raise SystemExit(f"geometry changed: {part['part_id']}")
        source_rows.append({"part_id":part["part_id"],"architecture_id":ARCH,"binding_id":part["binding_id"],"prior_drawing_path":part["drawing_path"],"prior_drawing_sha256":part["drawing_sha256"],"successor_drawing_path":f"cad/hr-v0/generated/mechanical-shop-drawing-p0.2/{new_name}","successor_drawing_sha256":digest(new_drawing),"step_path":part["step_path"],"step_sha256":part["step_sha256"],"dxf_path":part["dxf_path"],"dxf_sha256":part["dxf_sha256"],"geometry_fingerprint":new_fp,"geometry_changed":"FALSE","warning":WARNING})
        title_rows.append({"part_id":part["part_id"],"drawing_number":f"HRV0-{part['part_id']}-SD-P0.2","revision":"P0.2","sheet":"1 OF 1","units":"mm","scale":"NTS","material_candidate":part["material_candidate"],"finish":"BARE AS-MACHINED","architecture":ARCH,"formal_gdt_state":"SELECTION REQUIRED","fabrication_authorized":"FALSE","warning":WARNING})
        for kind, path_value, hash_value in (("SHOP DRAWING",f"cad/hr-v0/generated/mechanical-shop-drawing-p0.2/{new_name}",digest(new_drawing)),("FINISHED DXF",part["dxf_path"],part["dxf_sha256"]),("STEP",part["step_path"],part["step_sha256"])):
            payload_rows.append({"payload_id":f"RFQ-{index:02d}-{kind.replace(' ','-')}","part_id":part["part_id"],"quantity":"1","artifact_class":kind,"path":path_value,"sha256":hash_value,"transmission_authorized":"FALSE","provider_response":"NOT SENT / NO RESPONSE","warning":WARNING})
        shutil.copy2(new_drawing, REL / new_name)

    common = lambda rows: [dict(row, warning=WARNING) for row in rows]
    datasets: dict[str, tuple[list[str], list[dict[str, object]]]] = {}
    datasets["source-binding.csv"] = (["part_id","architecture_id","binding_id","prior_drawing_path","prior_drawing_sha256","successor_drawing_path","successor_drawing_sha256","step_path","step_sha256","dxf_path","dxf_sha256","geometry_fingerprint","geometry_changed","warning"], source_rows)
    datasets["title-block-register.csv"] = (["part_id","drawing_number","revision","sheet","units","scale","material_candidate","finish","architecture","formal_gdt_state","fabrication_authorized","warning"], title_rows)
    datasets["rfq-payload-manifest.csv"] = (["payload_id","part_id","quantity","artifact_class","path","sha256","transmission_authorized","provider_response","warning"], payload_rows)
    datasets["administrative-correction-register.csv"] = (["correction_id","subject","prior_state","successor_state","geometry_effect","closure_state","warning"], common([
        {"correction_id":"ADM-001","subject":"architecture identifier printed on five drawings","prior_state":"HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE","successor_state":ARCH,"geometry_effect":"NONE","closure_state":"CORRECTED IN SUCCESSOR"},
        {"correction_id":"ADM-002","subject":"artifact warning","prior_state":OLD_WARNING,"successor_state":WARNING,"geometry_effect":"NONE","closure_state":"CORRECTED IN SUCCESSOR"},
        {"correction_id":"ADM-003","subject":"drawing/revision/title block","prior_state":"identifier and candidate state only","successor_state":"drawing number, P0.2 revision, sheet, units, scale, material, source, geometry-change and authority fields","geometry_effect":"NONE","closure_state":"ADDED"},
        {"correction_id":"ADM-004","subject":"geometry source","prior_state":"P0.1 drawing plus exact STEP/DXF","successor_state":"same exact STEP/DXF and identical drawing geometry fingerprint","geometry_effect":"NONE","closure_state":"HASH PROVED"},
        {"correction_id":"ADM-005","subject":"formal datum reference frame and GD&T","prior_state":"ICF-01 CMM registration; not a released ASME Y14.5 DRF","successor_state":"ICF-01 retained; formal DRF/FCFs explicitly SELECTION REQUIRED","geometry_effect":"NONE","closure_state":"OPEN - QUALIFIED REVIEW REQUIRED"},
    ]))
    datasets["datum-gdt-disposition.csv"] = (["part_id","primary_face_candidate","in_plane_registration","current_numeric_control","formal_datum_reference_frame","feature_control_frames","qualified_disposition","fabrication_effect","warning"], common([
        {"part_id":p,"primary_face_candidate":"+Y broad face; non-countersink face where present","in_plane_registration":"ICF-01 rigid least-squares fit of four small interface-hole centers; no scale; report residuals","current_numeric_control":"Existing coordinate/profile/flatness/parallelism controls retained","formal_datum_reference_frame":"SELECTION REQUIRED","feature_control_frames":"SELECTION REQUIRED","qualified_disposition":"NOT EXECUTED","fabrication_effect":"BLOCKS FABRICATION RELEASE"} for p in ("MV0-C01","MV0-C04","MV0-C05","MV0-C06","MV0-C07")
    ]))
    datasets["rfq-cover-sheet.csv"] = (["part_id","quantity","part_name","material_candidate","process_candidate","drawing_number","included_files","quote_assumption_rule","commercial_state","warning"], common([
        {"part_id":p["part_id"],"quantity":"1","part_name":p["part_name"],"material_candidate":p["material_candidate"],"process_candidate":p["process_candidate"],"drawing_number":f"HRV0-{p['part_id']}-SD-P0.2","included_files":"successor SVG + exact finished DXF + exact STEP","quote_assumption_rule":"List every deviation/substitution separately; no silent portal healing, slotting, filing, pattern shift or material substitution","commercial_state":"RFQ PREPARATION ONLY - TRANSMISSION NOT AUTHORIZED"} for p in bindings
    ]))
    questions = [
        "Bind the quotation and every DFM response to all fifteen exact file hashes and five drawing numbers.",
        "Confirm the exact alloy/temper/specification, stock condition, finished-thickness range, heat-lot traceability and MTR availability.",
        "Confirm whether the five parts can be completed in-house under one controlled process route; identify every subcontracted operation.",
        "List any portal healing, automatic fillet/radius, tolerance, datum, finish or material default before quotation.",
        "Confirm all through-hole, countersink, profile, rail, recess, flatness, parallelism and edge-break controls are measurable as written.",
        "Propose a formal datum reference frame and feature-control-frame scheme without changing nominal geometry or current functional intent.",
        "State CMM/optical/pin-gauge capability, measurement uncertainty and calibration traceability for every proposed FAI characteristic.",
        "For MV0-C04, confirm the asymmetric H104 pattern will not be shifted, slotted or best-fit altered.",
        "For MV0-C05, describe the workholding and datum-transfer method between the S102 and column interfaces.",
        "For MV0-C06, describe how both striker rails and their relative height/location will be measured and reported.",
        "For MV0-C07, describe how the 1.000 mm recess and rail coplanarity will be measured and reported.",
        "For countersunk parts, confirm the received-head functional-gauge plan and residual-material measurement.",
        "State first-article segregation, raw-data retention, nonconformance, concession and rework controls.",
        "Acknowledge that capability review and budgetary quotation do not authorize fabrication or material purchase.",
    ]
    datasets["provider-capability-questionnaire.csv"] = (["question_id","question","response","exception_or_substitution","provider","responder","response_date","internal_disposition","transmission_authorized","warning"], common([{"question_id":f"RFQ-Q{i:02d}","question":q,"response":"NOT SENT / NO RESPONSE","exception_or_substitution":"NONE RECORDED","provider":"SELECTION REQUIRED","responder":"SELECTION REQUIRED","response_date":"SELECTION REQUIRED","internal_disposition":"NOT REVIEWED","transmission_authorized":"FALSE"} for i,q in enumerate(questions,1)]))

    steps = [
        ("AUTHORITY","Verify separate written unpowered-assembly authorization, exact commit and package hashes before touching hardware.","Signed scope/configuration authorization","STOP"),
        ("ENERGY CONTROL","Physically exclude all electrical sources, batteries and actuator-power leads; apply visible zero-energy tags.","Independent absence-of-energy witness","STOP"),
        ("RECEIVING","Match all five custom parts, purchased frames, actuators and candidate fasteners to receiving records.","Identity/hash/lot register","STOP"),
        ("INSPECTION","Accept material certificate and all thirty FAI operations before using any custom part.","Signed FAI disposition","STOP"),
        ("A00","Dry-fit MV0-C05 to the 40-4040 column T-slot with 17-8520/13035 candidates finger-tight only.","Photos; no-force fit; stack measurements","HOLD"),
        ("A00","Dry-fit J1 S102 to MV0-C05 using SCB2.5-20/HNN-M2.5-A2 candidates finger-tight only.","Four-hole alignment and tool-access record","HOLD"),
        ("A01","Dry-fit J1 H101 to MV0-C01 finger-tight only.","Four-hole alignment record","HOLD"),
        ("A02","Dry-fit MV0-C01 to the upper 20-2040 member and verify both M5 heads seat within the drawing limits.","End-tap depth/thread gauge and seating record","HOLD"),
        ("A03","Dry-fit MV0-C07 to the opposite upper-member end.","End-tap depth/thread gauge and seating record","HOLD"),
        ("A04","Dry-fit J2 S102 to MV0-C07 finger-tight only.","Four-hole alignment and catch orientation record","HOLD"),
        ("A05","Dry-fit J2 H101 to MV0-C06 finger-tight only.","Four-hole alignment and striker orientation record","HOLD"),
        ("A06","Dry-fit MV0-C06 and MV0-C04 to opposite forearm-member ends.","Both end interfaces and head seating record","HOLD"),
        ("A07","Dry-fit H104 to MV0-C04 finger-tight only.","Asymmetric four-hole alignment and orientation record","HOLD"),
        ("CHAIN","Join the loose subassemblies in the controlled P0.8 transform order without forcing alignment.","Full-chain photos and deviation log","HOLD"),
        ("ACCESS","Sweep required driver/wrench access; inspect cable, guard, service and pinch-clearance envelopes unpowered.","Tool/cable/guard clearance record","HOLD"),
        ("STOP","Manually approach HS-J2-POS with actuator torque disabled; verify intended rail-to-rail sequence without impact.","Contact witness, gap map and zero-impact record","HOLD"),
        ("TORQUE PLAN","Populate only qualified, fastener-lot-specific torque/locking/reuse values; do not infer catalog defaults.","Approved joint-control sheet","STOP"),
        ("TIGHTENING","Apply the approved staged tightening sequence only after all loose-fit holds pass.","Calibrated tool ID and as-built torque record","STOP"),
        ("METROLOGY","Measure assembled joint axes, hard-stop gap/contact, mass and center of mass; update inertia model.","As-built metrology and mass-property ledger","HOLD"),
        ("FINAL INSPECTION","Verify witness marks, retention, labels, guards and zero installed electrical energy.","Signed unpowered inspection","HOLD"),
        ("DISPOSITION","Qualified reviewer accepts, rejects or requires revision; quarantine the article until signed.","Configuration-bound decision","STOP"),
    ]
    datasets["unpowered-assembly-sequence.csv"] = (["step_id","interface_or_phase","instruction","required_evidence","hold_behavior","execution_state","assembly_authorized","warning"], common([{"step_id":f"UA-{i:02d}","interface_or_phase":phase,"instruction":inst,"required_evidence":evidence,"hold_behavior":hold,"execution_state":"NOT EXECUTED","assembly_authorized":"FALSE"} for i,(phase,inst,evidence,hold) in enumerate(steps,1)]))

    joint_data = [
        ("A00","MV0-C05 / 40-4040 / J1 S102","17-8520 + 13035; SCB2.5-20 + HNN-M2.5-A2","SELECTION REQUIRED","column slip, pullout, prying, S102 fit, tool access"),
        ("A01","J1 H101 / MV0-C01","SCB2.5-20 + HNN-M2.5-A2","SELECTION REQUIRED","pattern fit, protrusion, prevailing torque, tool access"),
        ("A02","MV0-C01 / upper 20-2040","SHKL-M5-20-A2-R360 / 20-7047","SELECTION REQUIRED","end-tap depth, engagement, head seating, locking"),
        ("A03","upper 20-2040 / MV0-C07","SHKL-M5-20-A2-R360 / 20-7047","SELECTION REQUIRED","end-tap depth, engagement, head seating, locking"),
        ("A04","MV0-C07 / J2 S102","SCB2.5-20 + HNN-M2.5-A2","SELECTION REQUIRED","pattern fit, protrusion, orientation, tool access"),
        ("A05","J2 H101 / MV0-C06","SCB2.5-20 + HNN-M2.5-A2","SELECTION REQUIRED","pattern fit, protrusion, orientation, tool access"),
        ("A06","forearm 20-2040 / MV0-C06 / MV0-C04","SHKL-M5-20-A2-R360 / 20-7047","SELECTION REQUIRED","both end taps, engagement, seating, locking"),
        ("A07","MV0-C04 / H104","SCB2.5-20 + HNN-M2.5-A2","SELECTION REQUIRED","asymmetric pattern, protrusion, orientation, tool access"),
        ("HS-J2-POS","MV0-C06 striker / MV0-C07 catch","integral rails; bumper SELECTION REQUIRED","NOT APPLICABLE UNTIL BUMPER SELECTED","gap, contact sequence, local stress, impact, life, overtravel"),
    ]
    datasets["joint-verification-matrix.csv"] = (["interface","members","candidate_hardware","torque_or_preload","required_physical_evidence","verification_state","motion_credit","warning"], common([{"interface":a,"members":b,"candidate_hardware":c,"torque_or_preload":d,"required_physical_evidence":e,"verification_state":"NOT EXECUTED","motion_credit":"NONE"} for a,b,c,d,e in joint_data]))
    tool_data = [
        ("TOOL-01","T25 driver bit for SHKL M5","Exact bit/reach and torque tool","SELECTION REQUIRED"),("TOOL-02","2 mm hex for M2.5 SHCS","Exact bit/reach and torque tool","SELECTION REQUIRED"),("TOOL-03","5 mm wrench for M2.5 locknut","Exact profile/reach","SELECTION REQUIRED"),("TOOL-04","6 mm hex for 17-8520 M8","Exact bit/reach and torque tool","SELECTION REQUIRED"),("TOOL-05","calibrated torque instruments","Range/accuracy/calibration for each selected joint","SELECTION REQUIRED"),("TOOL-06","pin gauges","2.70/5.50/8.50 feature acceptance set and calibration","SELECTION REQUIRED"),("TOOL-07","micrometer and caliper","Thickness/envelope range, resolution and calibration","SELECTION REQUIRED"),("TOOL-08","CMM or optical comparator","Coordinate/profile method and uncertainty","SELECTION REQUIRED"),("TOOL-09","surface plate/indicator","Flatness/parallelism method and calibration","SELECTION REQUIRED"),("TOOL-10","feeler/gap/contact witness set","Hard-stop gap/contact method and calibration","SELECTION REQUIRED"),("CONS-01","fastener locking material","Use only received pre-applied locking or separately qualified selection; do not mix","SELECTION REQUIRED"),("CONS-02","anti-galling control","Stainless joint-specific method","SELECTION REQUIRED"),
    ]
    datasets["tooling-consumables.csv"] = (["item_id","function","requirement","selection_state","received_state","use_authorized","warning"], common([{"item_id":a,"function":b,"requirement":c,"selection_state":d,"received_state":"NOT RECEIVED","use_authorized":"FALSE"} for a,b,c,d in tool_data]))
    ncr_steps = [
        ("NCR-01","Detect mismatch, damage, failed measurement, forced-fit tendency or undocumented substitution.","STOP AND SEGREGATE"),("NCR-02","Photograph and identify exact part/lot/tool/configuration without rework.","RECORD"),("NCR-03","Open a numbered nonconformance tied to drawing, characteristic and actual result.","RECORD"),("NCR-04","Prohibit filing, slotting, bending, chasing, shimming, force, material substitution or portal healing.","NO REWORK"),("NCR-05","Obtain design/qualified-review disposition: reject, use-as-is concession, or controlled rework instruction.","SELECTION REQUIRED"),("NCR-06","If revised, regenerate affected drawings, hashes, BOM/configuration and dependent analyses.","NEW REVISION"),("NCR-07","Reinspect all affected characteristics and preserve before/after evidence.","NOT EXECUTED"),("NCR-08","Release quarantine only with signed configuration-bound acceptance and separate work authority.","NOT AUTHORIZED"),
    ]
    datasets["nonconformance-workflow.csv"] = (["step_id","required_action","state","owner","evidence","warning"], common([{"step_id":a,"required_action":b,"state":c,"owner":"SELECTION REQUIRED","evidence":"NOT EXECUTED"} for a,b,c in ncr_steps]))
    holds = [
        ("R247-H01","Qualified mechanical drawing/GD&T disposition","Signed review of five successor drawings and formal DRF/FCFs"),("R247-H02","Authorized provider capability/DFM contact","Separate written scope and exact transmitted hash record"),("R247-H03","Provider DFM response","Complete answers and disposition of every exception"),("R247-H04","Material and process release","Exact specification/edition, heat lot, MTR, stock and process acceptance"),("R247-H05","Fastener/torque/locking/reuse release","Received lots, stack measurements, torque development and proof"),("R247-H06","Five-part first-article inspection","All thirty FAI operations with calibrated raw evidence"),("R247-H07","Unpowered assembly authorization","Separate scope/configuration authority with zero-energy controls"),("R247-H08","Unpowered full-chain fit","All 21 steps and nine joint rows accepted"),("R247-H09","Hard-stop bumper/contact/load/life closure","Exact bumper and physical/analytical proof"),("R247-H10","Structural and joint proof","Static, slip, pullout, prying, fatigue and proof cases"),("R247-H11","Mass/COM/inertia reconciliation","Received moving-item and assembly metrology"),("R247-H12","Immutable configuration and qualified release","Merged clean-clone baseline and signed decision"),
    ]
    datasets["open-holds.csv"] = (["hold_id","hold","state","closure_evidence","fabrication_effect","warning"], common([{"hold_id":a,"hold":b,"state":"OPEN","closure_evidence":c,"fabrication_effect":"BLOCKS FABRICATION/ASSEMBLY RELEASE"} for a,b,c in holds]))
    acceptance = [
        "Five successor drawing hashes and geometry fingerprints reproduce from the exact P0.3 binding.","Qualified reviewer accepts formal datum reference frames and feature-control frames.","Authorized provider returns complete hash-bound capability and DFM responses.","Material/process/finish and first-article plan are accepted.","All thirty first-article operations pass on segregated articles.","Every candidate fastener stack, torque, locking, reuse and tool-access control is accepted.","All twenty-one unpowered assembly steps and nine joint checks pass without force or rework.","Hard-stop, structural, mass/COM/inertia and full-chain clearance evidence is accepted.","Nonconformance workflow and configuration supersession are accepted.","Separate written fabrication/assembly authority is issued by the required roles.",
    ]
    datasets["acceptance-matrix.csv"] = (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], common([{"acceptance_id":f"R247-ACC-{i:02d}","criterion":v,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,v in enumerate(acceptance,1)]))

    for name,(fields,rows) in datasets.items(): write_csv(SRC / name, fields, rows)
    status = {"identifier":IDENT,"drawing_identifier":DRAW_IDENT,"round":"R247","date":"2026-08-11","architecture":ARCH,"binding":BIND_IDENT,"status":"REVIEW/RFQ PREPARATION ONLY","part_count":5,"successor_drawing_count":5,"payload_artifact_count":15,"geometry_changes":0,"administrative_corrections":5,"formal_gdt_released":False,"provider_questions":14,"provider_contacted":False,"unpowered_assembly_steps":21,"joint_verification_rows":9,"tooling_rows":12,"open_holds":12,"acceptance_rows":10,"physical_article_exists":False,"qualified_review_complete":False,"quotation_authorized":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (SRC / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (SRC / "README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nFive successor shop-drawing candidates correct the printed architecture identity, warning and title-block/revision control while preserving exact P0.3 STEP/DXF geometry. The package supplies a 15-artifact RFQ manifest and a 21-step unpowered assembly definition. Formal GD&T, provider contact, physical work and every authority remain open.\n",encoding="utf-8",newline="\n")
    for path in SRC.iterdir():
        if path.is_file() and path.name != "file-manifest.csv": shutil.copy2(path, REL / path.name)
    csv_names = list(datasets)
    (REL / "index.html").write_text(make_page("HR-V0 mechanical shop, RFQ and unpowered assembly candidate","Five corrected shop drawings, one exact RFQ payload and a fail-closed part-by-part assembly traveler.",REL,csv_names),encoding="utf-8",newline="\n")
    manifest(SRC); manifest(REL)


def generate_config() -> None:
    for directory in (CFG,CFG_REL):
        if directory.exists(): shutil.rmtree(directory)
        shutil.copytree(CFG_OLD,directory)
    current,fields=read_csv(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-31","role":"mechanical shop/RFQ/unpowered assembly candidate","identifier":IDENT,"source_path":"release/hr-v0/mechanical-shop-rfq-assembly-p0.1/package-status.json","configuration_state":"CURRENT SUPPORTING CANDIDATE - REVIEW/RFQ PREPARATION ONLY","release_boundary":"five successor drawings and exact payload; formal GD&T, provider response, FAI, physical/qualified evidence and work authority open","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",fields,current)
    supersession,fields=read_csv(CFG/"supersession-map.csv")
    supersession.append({"record_id":"SUP-18","prior_identifier":"HR-V0-CONFIG-REC-P0.10","current_or_required_successor":CFG_IDENT,"disposition":"SUPERSEDED BY R247 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG/"supersession-map.csv",fields,supersession)
    holds,fields=read_csv(CFG/"open-holds.csv")
    holds.extend([
        {"hold_id":"HOLD-42","hold":"Five successor shop drawings and formal datum/GD&T qualified disposition","state":"NOT EXECUTED","closure_evidence":"Signed review against exact drawing/STEP/DXF hashes","warning":WARNING},
        {"hold_id":"HOLD-43","hold":"Authorized provider capability/DFM response against exact R247 payload","state":"NOT EXECUTED","closure_evidence":"Transmission record, response and internal disposition","warning":WARNING},
        {"hold_id":"HOLD-44","hold":"Five custom-part first articles and fastener/joint evidence","state":"NOT EXECUTED","closure_evidence":"MTR, 30 FAI operations, stacks, torque/locking and proof","warning":WARNING},
        {"hold_id":"HOLD-45","hold":"Configuration-bound unpowered full-arm assembly and qualified acceptance","state":"NOT EXECUTED","closure_evidence":"21-step traveler, nine joint rows, mass/COM/inertia, clearances and signed disposition","warning":WARNING},
    ])
    write_csv(CFG/"open-holds.csv",fields,holds)
    acceptance,fields=read_csv(CFG/"acceptance-matrix.csv")
    criteria=["R247 successor drawing/admin parity reproduced","R247 formal datum/GD&T accepted","R247 RFQ payload independently hash-verified","R247 provider DFM response accepted","R247 five-part FAI passed","R247 fastener/joint controls accepted","R247 unpowered assembly traveler passed","R247 qualified configuration release signed"]
    for number,criterion in enumerate(criteria,58): acceptance.append({"acceptance_id":f"ACC-{number:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"acceptance-matrix.csv",fields,acceptance)
    impacts,fields=read_csv(CFG/"gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-002","EG-003","EG-005","EG-006"}:
            row["evidence_added"] += f"; {IDENT} successor drawings/RFQ/unpowered assembly definition"
            row["remaining_evidence"] += "; formal GD&T, provider DFM, FAI, physical assembly/proof and qualified release"
            row["gate_closed"]="NO"
    write_csv(CFG/"gate-impact.csv",fields,impacts)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CFG_IDENT,"round":"R247","current_records":31,"supersession_records":18,"open_holds":45,"acceptance_rows":65,"mechanical_shop_rfq_assembly":IDENT})
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR247 carries P0.10 forward and adds the review/RFQ-preparation-only mechanical shop and unpowered assembly candidate. P1.15 remains current; P1.21 remains unaccepted. Forty-five holds and sixty-five unexecuted acceptance rows remain.\n",encoding="utf-8",newline="\n")
    source_rows=[]
    for row in current:
        path=ROOT/row["source_path"]
        if not path.is_file(): raise SystemExit(f"missing config source: {path}")
        source_rows.append({"source_path":row["source_path"],"sha256":digest(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],source_rows)
    manifest(CFG)
    for path in CFG.iterdir():
        if path.is_file() and path.name!="file-manifest.csv": shutil.copy2(path,CFG_REL/path.name)
    csv_names=["current-configuration-map.csv","supersession-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv"]
    (CFG_REL/"index.html").write_text(make_page("HR-V0 configuration reconciliation P0.11","Current identifiers, open holds and acceptance requirements after the R247 mechanical shop/RFQ/assembly candidate.",CFG_REL,csv_names),encoding="utf-8",newline="\n")
    manifest(CFG_REL)


def main() -> None:
    generate_package(); generate_config(); write_generated_source_manifest()
    print(f"Generated {IDENT} and {CFG_IDENT}: five drawings, zero geometry changes, 15 payload artifacts, 21 unpowered steps, no work authority")


if __name__ == "__main__": main()
