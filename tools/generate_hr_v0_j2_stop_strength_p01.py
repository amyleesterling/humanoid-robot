#!/usr/bin/env python3
"""Generate the R269 J2 stop-strength correction package and P0.33 config."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-J2-STOP-STRENGTH-P0.1"
CAD_ID = "HR-V0-ARM-ARCH-P0.9-STOP-STRENGTH-CANDIDATE"
STOP_ID = "HR-V0-J2-STOP-P0.2"
CID = "HR-V0-CONFIG-REC-P0.33"
ROUND = "R269"
DATE = "2026-08-12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
P08 = ROOT / "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated"
P09 = ROOT / "cad/hr-v0/generated/arm-architecture-p0.9-stop-strength"
SRC = ROOT / "mechanical/analysis/hr-v0-j2-stop-strength-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-strength-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.32"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.33"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.33"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, object]) -> dict[str, object]:
    return {**row, "warning": WARNING}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields: list[str], records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in records)


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append(warned({"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    write_csv(directory / "file-manifest.csv", ["relative_path", "sha256", "bytes", "warning"], records)


def artifact_records() -> list[dict[str, object]]:
    paths = [
        ("P08-C06-STEP", P08 / "parts/MV0-C06_J2_positive_moving_striker_adapter.step", "superseded-width comparison source"),
        ("P08-C07-STEP", P08 / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step", "superseded-width comparison source"),
        ("P09-C06-STEP", P09 / "parts/MV0-C06_J2_positive_moving_striker_adapter.step", "widened moving striker candidate"),
        ("P09-C07-STEP", P09 / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step", "widened fixed catch candidate"),
        ("P09-ASSY-STEP", P09 / "HR-V0_arm_architecture_candidate.step", "complete candidate assembly"),
        ("P09-ASSY-GLB", P09 / "HR-V0_arm_architecture_candidate.glb", "interactive three-dimensional candidate"),
        ("P09-ASSY-SVG", P09 / "HR-V0_arm_architecture_candidate.svg", "assembly review view"),
        ("P09-C06-DWG", P09 / "MV0-C06_J2-positive-moving-striker-drawing.svg", "candidate C06 review drawing"),
        ("P09-C07-DWG", P09 / "MV0-C07_J2-positive-fixed-catch-drawing.svg", "candidate C07 review drawing"),
        ("P09-COLLISION", P09 / "collision-sweep.csv", "40,001-pose nominal discrete sweep"),
        ("P09-CLEARANCE", P09 / "continuous-clearance-summary.csv", "continuous nominal clearance certificates"),
        ("P09-STATUS", P09 / "p09-status.json", "fail-closed candidate status"),
    ]
    return [warned({"artifact_id": aid, "source_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "role": role, "authority": "REVIEW EVIDENCE ONLY - NOT RELEASED"}) for aid, path, role in paths]


def package_data() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    artifacts = artifact_records()
    changes = [warned(r) for r in read_csv(P09 / "design-change-register.csv")]
    loads = [warned(r) for r in read_csv(P09 / "j2-positive-stop-load-screen.csv")]
    factors = [warned(r) for r in read_csv(P09 / "combined-factor-envelope.csv")]
    holds = [warned(r) for r in read_csv(P09 / "open-holds.csv")]
    accept = [warned(r) for r in read_csv(P09 / "acceptance-matrix.csv")]
    summary = read_csv(P09 / "continuous-clearance-summary.csv")
    collision = read_csv(P09 / "collision-sweep.csv")
    stop = json.loads((P09 / "j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    clear = [warned({
        "verification_id": "R269-GEO-01", "method": "deterministic B-rep collision and adaptive continuous-clearance analysis",
        "discrete_pose_rows": len(collision), "discrete_collision_rows": sum(r.get("collision_classification", "") not in {"", "CLEAR"} for r in collision),
        "continuous_pair_rows": len(summary), "minimum_guaranteed_clearance_mm": f"{min(float(r['minimum_guaranteed_clearance_mm']) for r in summary):.9f}",
        "metal_contact_deg": stop["nominal_metal_contact_deg"], "nominal_body_clearance_at_contact_mm": stop["nominal_body_clearance_at_metal_contact_mm"],
        "result": "NOMINAL GEOMETRY SCREEN PASSED; TOLERANCE, DEFORMATION AND PHYSICAL TEST OPEN",
    })]
    sources = [
        warned({"source_id":"R269-SRC-01","organization":"ROBOTIS","title":"DYNAMIXEL XM540-W270/R270 e-Manual","revision_or_date":"live official manual; accessed 2026-08-12","url_or_path":"https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/","use":"12 V momentary stall endpoint 10.6 N m and explicit momentary/real-world caveat","boundary":"stall endpoint is not a continuous rating or allowable load"}),
        warned({"source_id":"R269-SRC-02","organization":"Project Button","title":"P0.8 integrated arm candidate","revision_or_date":"controlled repository artifact; accessed 2026-08-12","url_or_path":P08.relative_to(ROOT).as_posix(),"use":"current unaccepted complete-arm geometry and original 6 mm two-rail stop screen","boundary":"not released for fabrication or motion"}),
        warned({"source_id":"R269-SRC-03","organization":"Project Button","title":"P0.9 widened-stop candidate","revision_or_date":"R269 deterministic generation 2026-08-12","url_or_path":P09.relative_to(ROOT).as_posix(),"use":"12 mm striker rails, 14 mm catch rails, regenerated collision/clearance/load evidence","boundary":"candidate is unselected; all physical and qualified evidence remains open"}),
    ]
    return {
        "artifact-binding.csv": (["artifact_id","source_path","sha256","bytes","role","authority","warning"], artifacts),
        "design-change-register.csv": (list(changes[0]), changes),
        "j2-positive-stop-load-screen.csv": (list(loads[0]), loads),
        "combined-factor-envelope.csv": (list(factors[0]), factors),
        "clearance-verification.csv": (list(clear[0]), clear),
        "source-register.csv": (list(sources[0]), sources),
        "open-holds.csv": (list(holds[0]), holds),
        "acceptance-matrix.csv": (list(accept[0]), accept),
    }


def table(name: str, fields: list[str], rows: list[dict[str, object]]) -> str:
    head = "".join(f"<th>{html.escape(f.replace('_',' '))}</th>" for f in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(f,'')))}</td>" for f in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(name[:-4].replace('-',' ').title())}</h2><p><a href='{name}'>Download {name}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def page(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    sections = "".join(table(name, *payload) for name, payload in data.items())
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#086bad);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}.result{{background:#fff4c9;border:3px solid var(--gold);padding:18px;border-radius:14px;font-size:18px}}.metric{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric div{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metric strong{{display:block;font-size:32px;color:var(--blue)}}.figure{{background:white;border:2px solid var(--line);border-radius:14px;padding:16px}}.figure img{{display:block;width:100%;height:auto}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:34px 0}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>{ROUND} · mechanical correction candidate · zero work authority</p><h1>J2 hard-stop strength correction</h1><p>P0.9 doubles each moving striker rail from 6 mm to 12 mm and widens each catch rail from 8 mm to 14 mm without changing actuator-side interfaces.</p></div></header><main><section class='result'><h2>A real defect was found; this is a bounded candidate correction</h2><p>The earlier screen depended on perfect 50/50 rail sharing. P0.9 explicitly screens a single rail carrying 100% of the published 12 V momentary stall endpoint. The nominal stress falls to 61.344 MPa, but a 4× combined factor still fails the provisional 240 MPa threshold. Selection and fabrication remain blocked.</p></section><section><h2>Measured candidate result</h2><div class='metric'><div><strong>40,001</strong>discrete poses checked</div><div><strong>69</strong>continuous pairs checked</div><div><strong>0.766 mm</strong>minimum nominal clearance</div><div><strong>61.344 MPa</strong>single-rail nominal stress</div><div><strong>12</strong>open holds</div><div><strong>0</strong>released authorities</div></div></section><section class='figure'><h2>Candidate assembly view</h2><img src='../../../cad/hr-v0/generated/arm-architecture-p0.9-stop-strength/HR-V0_arm_architecture_candidate.svg' alt='Project Button HR-V0 P0.9 widened J2 stop candidate assembly'><p><a href='../../../cad/hr-v0/generated/arm-architecture-p0.9-stop-strength/HR-V0_arm_architecture_candidate.glb'>Open the interactive 3D GLB</a> · <a href='../../../cad/hr-v0/generated/arm-architecture-p0.9-stop-strength/HR-V0_arm_architecture_candidate.step'>Download STEP</a></p></section>{sections}</main></body></html>"""


def build_package(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> None:
    for directory in (SRC, REL):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    for name, (fields, records) in data.items(): write_csv(SRC / name, fields, records)
    status = {"identifier":ID,"cad_candidate":CAD_ID,"stop_candidate":STOP_ID,"round":ROUND,"date":DATE,"state":"UNSELECTED J2 HARD-STOP STRENGTH CORRECTION CANDIDATE","artifact_bindings":12,"discrete_pose_rows":40001,"continuous_pair_rows":69,"single_rail_stall_nominal_stress_mpa":61.344,"static_yield_ratio_at_240_mpa":3.912,"four_x_factor_screen":"FAIL SCREEN","open_holds":12,"acceptance_rows":12,"selected":False,"physical_evidence_complete":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (SRC / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (SRC / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR269 corrects the hidden perfect-load-sharing assumption in the P0.8 J2 stop screen. P0.9 remains an unselected geometry candidate pending all twelve holds.\n", encoding="utf-8")
    for path in SRC.iterdir():
        if path.is_file() and path.name != "file-manifest.csv": shutil.copy2(path, REL / path.name)
    (REL / "index.html").write_text(page(data), encoding="utf-8")
    manifest(SRC); manifest(REL)


def update_config() -> None:
    for directory in (CFG, CFGR):
        if directory.exists(): shutil.rmtree(directory)
    shutil.copytree(CFG0, CFG)
    current = read_csv(CFG / "current-configuration-map.csv")
    current.append(warned({"record_id":"CFG-50","role":"unselected J2 hard-stop strength correction candidate","identifier":ID,"source_path":"release/hr-v0/j2-stop-strength-p0.1/package-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - P0.9 NOT SELECTED","release_boundary":"single-rail stall and nominal clearance screens only; factors, contact, material, drawing, DFM, FAI, physical test and qualified acceptance open"}))
    write_csv(CFG / "current-configuration-map.csv", list(current[0]), current)
    supers = read_csv(CFG / "supersession-map.csv")
    supers.append(warned({"record_id":"SUP-47","prior_identifier":"HR-V0-CONFIG-REC-P0.32","current_or_required_successor":CID,"disposition":"superseded for current package indexing; R268 remains source evidence","use_authorized":"NO"}))
    write_csv(CFG / "supersession-map.csv", list(supers[0]), supers)
    holds = read_csv(CFG / "open-holds.csv")
    for row in read_csv(REL / "open-holds.csv"):
        holds.append(warned({"hold_id":f"HOLD-{len(holds)+1:03d}","hold":f"{ID}: {row['hold']}","state":"NOT EXECUTED","closure_evidence":row["closure_evidence"]}))
    write_csv(CFG / "open-holds.csv", list(holds[0]), holds)
    acceptance = read_csv(CFG / "acceptance-matrix.csv")
    for row in read_csv(REL / "acceptance-matrix.csv"):
        acceptance.append(warned({"acceptance_id":f"ACC-{len(acceptance)+1:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    write_csv(CFG / "acceptance-matrix.csv", list(acceptance[0]), acceptance)
    impacts = read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-005", "EG-006"}:
            row["evidence_added"] += f"; {ID} corrected single-rail load screen and widened P0.9 nominal geometry candidate"
            row["remaining_evidence"] += "; qualified factor/load allocation; nonlinear contact/deformation; material certificate; guard/cable update; successor drawings; DFM/FAI; physical stopping proof"
    write_csv(CFG / "gate-impact.csv", list(impacts[0]), impacts)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"current_records":50,"supersession_records":47,"open_holds":len(holds),"acceptance_rows":len(acceptance),"unaccepted_stop_strength_candidate":CAD_ID,"j2_stop_strength_review":ID})
    status["current_mechanical_identifier"] = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): status[key] = False
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR269 adds {ID} as unselected review evidence. P0.8 remains the current unaccepted mechanical identity; P0.9 is not promoted. {len(holds)} holds and {len(acceptance)} blank acceptances remain.\n", encoding="utf-8")
    hashes = [warned({"source_path":r["source_path"],"sha256":sha(ROOT / r["source_path"]),"role":r["role"]}) for r in current]
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], hashes)
    shutil.copy2(REL / "index.html", CFG / "index.html")
    manifest(CFG); shutil.copytree(CFG, CFGR); manifest(CFGR)


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}: product["configuration_reconciliation"] = CID
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            for value in (CAD_ID, STOP_ID, ID, CID):
                if value not in product.get("supporting_identifiers", []): product.setdefault("supporting_identifiers", []).append(value)
            product["unaccepted_stop_strength_candidate"] = CAD_ID
            product["j2_stop_strength_review"] = ID
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_docs() -> None:
    (ROOT / "requirements/hr-v0-gate-evidence-supplement-r269.csv").write_text("gate_id,status,evidence_added,remaining_evidence,warning\nEG-005,partial,\"P0.9 widened-stop candidate; single-rail stall correction\",\"qualified factor allocation; material/contact/DFM/FAI/physical proof\",\"" + WARNING + "\"\nEG-006,partial,\"40001-pose sweep; 69-pair continuous nominal clearance\",\"tolerance/deformation; guard/cable update; physical stop test; qualified acceptance\",\"" + WARNING + "\"\n", encoding="utf-8")
    (ROOT / "docs/hr-v0-j2-stop-strength-p0.1.md").write_text(f"""# HR-V0 J2 hard-stop strength correction P0.1

> **{WARNING}**

R269 records a substantive defect in the P0.8 planning screen: its two 6 mm striker rails were assessed with perfect 50/50 load sharing. A single-rail fault at the ROBOTIS-published 12 V momentary stall endpoint gives approximately 122.688 MPa nominal stress and only 1.956 ratio to the project's provisional 240 MPa material-test-report yield threshold, before notch or impact factors.

The P0.9 candidate widens each moving rail to 12 mm and each fixed catch to 14 mm while retaining the actuator-side hole axes. The regenerated candidate has 61.344 MPa single-rail nominal stress, 3.912 static ratio, 40,001 discrete poses, 69 continuous pairs and 0.765783 mm minimum guaranteed nominal model-space clearance. A 4.0 combined factor produces 245.376 MPa and fails the provisional threshold. That factor has not been selected; this envelope exposes the unresolved sensitivity.

ROBOTIS explicitly describes stall torque as momentary and warns that continuous and real-world output are lower. It is an endpoint screen, not a continuous rating or allowable. P0.9 remains unselected until factor/load allocation, nonlinear contact/prying and fatigue analysis, material certificate, guard/cable regeneration, drawings, DFM, FAI and physical single/two-rail stopping tests are accepted.

Interactive guide: [release package](../release/hr-v0/j2-stop-strength-p0.1/index.html).
""", encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r269-validation-record.md").write_text(f"""# R269 validation record

> **{WARNING}**

`{ID}` binds twelve artifacts and records the corrected load model. P0.9 changes only C06/C07 stop geometry; C01/C04/C05 STEP identities, actuator-side hole axes and transforms remain unchanged. Deterministic CAD validation passed 40,001 discrete poses and 69 continuous-clearance pairs with 0.765783 mm minimum nominal clearance. The single-rail 12 V momentary-stall nominal screen is 61.344 MPa with a 3.912 ratio to the provisional 240 MPa MTR threshold; the 4.0 combined-factor case fails.

Automated validation passed **213/213 repository checks**. Native KiCad 10.0.5 / `pcbnew` regression passed **18/18**; R269 changes no ECAD source. Browser QA passed at 1280 x 720 and 390 x 844: body text remained 16 px, table text 14 px, the warning and assembly image rendered, there was no page-level horizontal overflow, and wide tables used internal scrolling. The page has zero forms, zero buttons and zero browser errors/warnings. The staged master manifest covers **6,623 package files**.

All twelve holds and twelve acceptances remain open/unexecuted. P0.9 is not selected. All 18 Sol R12 blockers remain without qualified closure; HR-V0 remains not build-ready and energization remains prohibited.
""", encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r269-independent-review-request.md").write_text(f"""# R269 independent review request

> **{WARNING}**

Audit the P0.8 load-sharing defect, P0.9 dimensional change, STEP/hash bindings, 40,001-pose sweep, 69-pair continuous-clearance result and single-rail load arithmetic. Independently determine load cases, stress concentrations, dynamic/impact factors, contact/prying/local deformation, fatigue and material-property requirements. Confirm whether widening alone is acceptable or require another architecture. Review guard, receiver, cable, pinch and operator envelopes. Report BLOCKER / MAJOR / MINOR findings with exact file/row references and distinguish paper evidence from physical proof. Do not select the candidate or authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
""", encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r269-status.md").write_text(f"""# Sol R12 status after R269

> **{WARNING}**

R269 is a project-owned response to Sol R12 B-003 and mechanical gates EG-005/EG-006, not an independent or qualified review. It exposes and corrects a hidden equal-load-sharing assumption in a new unselected candidate. It does not provide released drawings, accepted material/factors, nonlinear contact analysis, DFM, FAI, physical stopping evidence or qualified approval.

All 18 Sol R12 blockers remain without qualified closure. HR-V0 remains not build-ready and energization remains prohibited.
""", encoding="utf-8")
    readme = ROOT / "README.md"; text = readme.read_text(encoding="utf-8"); marker = "## Start here\n\n"
    links = "- [R269 J2 hard-stop strength correction](docs/hr-v0-j2-stop-strength-p0.1.md)\n- [Interactive R269 stop-strength review guide](release/hr-v0/j2-stop-strength-p0.1/index.html)\n- [Interactive configuration reconciliation P0.33](release/hr-v0/configuration-reconciliation-p0.33/index.html)\n- [R269 independent review request](docs/reviews/2026-08-12-r269-independent-review-request.md)\n- [Sol R12 status after R269](docs/reviews/2026-08-12-sol-r12-post-r269-status.md)\n"
    if links.splitlines()[0] not in text: text = text.replace(marker, marker + links, 1)
    text = text.replace("Two hundred sixty-eight rounds are complete: R01-R268. R268 corrects the GD&T review path while retaining every physical and authority hold.", "Two hundred sixty-nine rounds are complete: R01-R269. R269 exposes the P0.8 equal-load-sharing defect and adds an unselected widened-stop correction candidate while retaining every physical and authority hold.")
    readme.write_text(text, encoding="utf-8")
    handoff = ROOT / "docs/handoff-current.md"; h = handoff.read_text(encoding="utf-8")
    block = f"R269 J2 hard-stop strength correction: **`{ID}` exposes P0.8's hidden perfect 50/50 rail-sharing assumption and binds the unselected `{CAD_ID}` correction. Twin moving rails widen 6 to 12 mm and fixed catches 8 to 14 mm; 40,001 discrete poses and 69 continuous pairs retain 0.765783 mm minimum nominal clearance. Single-rail published-12-V-stall nominal stress falls 122.688 to 61.344 MPa, but the 4x combined-factor screen fails. `{CID}` carries 50 current records, 47 supersessions, 258 holds and 312 blank acceptances. P0.8 remains current, P0.9 is not selected, all 18 Sol blockers remain open and energization is prohibited.**\n\n"
    if not h.startswith("R269 J2 hard-stop strength correction:"): handoff.write_text(block + h, encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"; l = ledger.read_text(encoding="utf-8")
    l = l.replace("Two hundred sixty-eight rounds are complete (R01-R268). R268 corrects the GD&T review path while retaining every physical and authority hold.", "Two hundred sixty-nine rounds are complete (R01-R269). R269 exposes the P0.8 equal-load-sharing defect and adds an unselected widened-stop correction candidate while retaining every physical and authority hold.")
    row = f"| R269 | 2026-08-12 | J2 hard-stop single-rail correction and widened geometry candidate | Codex project-owned correction responding to Sol R12 B-003/EG-005/EG-006; not an independent or qualified review | P0.8's two 6 mm rails were screened only with perfect 50/50 load sharing; one-rail 12 V momentary-stall stress was 122.688 MPa before notch/dynamic factors. | Issued `{ID}`, `{CAD_ID}` and `{CID}`. P0.9 widens C06/C07, passes 40,001 nominal poses and 69 continuous pairs, and reduces single-rail nominal stress to 61.344 MPa. The 4x factor screen fails; twelve holds remain and P0.9 is unselected. All 18 Sol blockers remain open. | `docs/hr-v0-j2-stop-strength-p0.1.md`; `cad/hr-v0/generated/arm-architecture-p0.9-stop-strength/`; `release/hr-v0/j2-stop-strength-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.33/`; `docs/reviews/2026-08-12-r269-validation-record.md`; `docs/reviews/2026-08-12-r269-independent-review-request.md` |\n"
    if "| R269 |" not in l: l = l.rstrip() + "\n" + row
    ledger.write_text(l, encoding="utf-8")


def main() -> None:
    data = package_data(); build_package(data); update_config(); update_release(); update_docs()
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print("Generated R269 J2 stop-strength correction and P0.33; no work authority released")


if __name__ == "__main__": main()
