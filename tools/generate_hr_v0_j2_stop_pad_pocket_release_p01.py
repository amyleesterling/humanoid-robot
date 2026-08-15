#!/usr/bin/env python3
"""Publish R278 exact-normal P0.13 stop analysis and P0.42 index."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-pad-pocket-fea-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-pad-pocket-fea-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.41"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.42"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.42"
IDENT = "HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1"
CAD_IDENT = "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.42"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    records = [{"relative_path":p.relative_to(directory).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING}
               for p in sorted(directory.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, object]]) -> str:
    fields = list(records[0]); head = "".join(f"<th>{html.escape(k.replace('_',' '))}</th>" for k in fields)
    body = "".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(k,'')))}</td>" for k in fields)+"</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    for target in (REL, CFG, CFG_REL):
        if target.exists(): shutil.rmtree(target)
    status = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    convergence = rows(FEA / "mesh-convergence.csv")
    boundaries = rows(FEA / "load-boundary-register.csv")
    holds = rows(FEA / "open-holds.csv")
    cases = status["cases"]
    c06 = cases["C06_EXACT_NORMAL_TOP"]
    perimeter = cases["C07_METAL_PERIMETER_EXACT_NORMAL"]
    floor = cases["C07_POCKET_FLOOR_EXACT_NORMAL"]

    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R278 exact-normal J2 stop analysis</title><script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js'></script><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--paper:#f7fbff;--line:#9ccfe8;--red:#9b1c1c;--green:#dff6ea}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(26px,3vw,40px);line-height:1.18;color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}}.card,.decision,.truth{{background:white;border:2px solid var(--line);border-radius:15px;padding:20px}}.card strong{{display:block;font-size:34px;color:var(--navy)}}.decision{{border-left:10px solid var(--gold)}}.truth{{background:var(--green);border-left:10px solid #188454}}.viewer{{border:3px solid var(--navy);border-radius:16px;overflow:hidden;background:var(--pale)}}model-viewer{{display:block;width:100%;height:clamp(470px,70vh,720px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p{{padding:14px 18px;background:white;margin:0}}.diagram-scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}.diagram{{display:block;width:100%;min-width:900px;height:auto}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}model-viewer{{height:480px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R278 &middot; {IDENT} &middot; corrected coordinates, linear screen only</p><h1>The stop load now follows the actual contact normal.</h1><p>The moving and fixed parts use equal-and-opposite forces transformed into their own coordinate systems. Metal-perimeter and pocket-floor transfers are separate.</p></div></header><main><section class='grid'><div class='card'><strong>{c06['finest_global_maximum_mpa']:.3f} MPa</strong>C06 exact-normal maximum</div><div class='card'><strong>{perimeter['finest_global_maximum_mpa']:.3f} MPa</strong>C07 pad-absent perimeter</div><div class='card'><strong>{floor['finest_global_maximum_mpa']:.3f} MPa</strong>C07 pocket-floor screen</div><div class='card'><strong>{min(c06['ratio_to_project_threshold'],perimeter['ratio_to_project_threshold'],floor['ratio_to_project_threshold']):.2f}×</strong>minimum arithmetic ratio to 240 MPa project threshold</div></section><section class='truth'><h2>All three nominal linear cases pass the internal geometry screen</h2><p>This means the exact P0.13 shape is not rejected by this limited linear model. It does <strong>not</strong> mean the stop is approved: 240 MPa is not a released allowable, and the model omits contact nonlinearity, the bolted/frame joint, dynamics, tolerances, fatigue and physical correlation.</p></section><section class='decision'><h2>R278 supersedes the earlier load-direction calculation</h2><p>The previous C06 screen used <code>[0, cos(q), -sin(q)]</code> rather than transforming the exact B-Rep normal; the previous C07 screen applied a pure Y load. R278 uses C06 local <code>[0, 0, -1]</code> and C07 fixed <code>[0, -0.882948, -0.469470]</code>, then treats the surrounding metal face and pocket floor separately.</p></section><section><h2>Inspect the P0.13 geometry</h2><div class='viewer'><model-viewer src='../../../cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/HR-V0_J2_C07_pad-pocket-installed-screen.glb' alt='Interactive 3D model of the P0.13 pocketed J2 fixed catch and nominal pads' camera-controls camera-orbit='35deg 70deg 90%' min-camera-orbit='auto auto 30%' max-camera-orbit='auto auto 320%' field-of-view='28deg' shadow-intensity='.8'></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Yellow pad solids are nominal visualization only.</p></div></section><section><h2>Coordinate correction</h2><div class='diagram-scroll'><svg class='diagram' viewBox='0 0 1100 500' role='img' aria-label='Equal and opposite contact-force vectors on C06 and C07'><defs><marker id='a' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'><path d='M0,0 L0,6 L9,3 z' fill='#082b55'/></marker></defs><rect x='80' y='90' width='310' height='300' rx='20' fill='#f4b942' stroke='#082b55' stroke-width='5'/><rect x='710' y='90' width='310' height='300' rx='20' fill='#7dd3fc' stroke='#082b55' stroke-width='5'/><text x='235' y='145' text-anchor='middle' font-size='30' font-weight='800' fill='#082b55'>C06 moving</text><text x='865' y='145' text-anchor='middle' font-size='30' font-weight='800' fill='#082b55'>C07 fixed</text><line x1='430' y1='260' x2='660' y2='150' stroke='#082b55' stroke-width='9' marker-end='url(#a)'/><line x1='670' y1='270' x2='440' y2='380' stroke='#082b55' stroke-width='9' marker-end='url(#a)'/><text x='550' y='115' text-anchor='middle' font-size='25' fill='#082b55'>equal and opposite 253.607 N</text><text x='235' y='315' text-anchor='middle' font-size='23' fill='#082b55'>local: [0, 0, −1]</text><text x='865' y='315' text-anchor='middle' font-size='23' fill='#082b55'>fixed: [0, −.882948, −.469470]</text><text x='550' y='455' text-anchor='middle' font-size='23' font-weight='800' fill='#9b1c1c'>direction corrected; contact and joint are still idealized</text></svg></div></section><section><h2>Load and boundary register</h2>{table(boundaries)}</section><section><h2>Mesh sensitivity</h2>{table(convergence)}</section><section><h2>Evidence still required</h2>{table(holds)}</section></main></body></html>"""
    (FEA / "README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR278 corrects the C06/C07 coordinate transforms and separately screens the P0.13 metal-perimeter and pocket-floor paths. All cases pass an internal linear geometry-rejection rule; no allowable, selection or work authority is released.\n",encoding="utf-8")
    (FEA / "index.html").write_text(page,encoding="utf-8")
    shutil.copytree(FEA, REL); manifest(FEA); manifest(REL)

    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-61","role":"P0.13 exact-normal C06/C07 metal-perimeter and pocket-floor linear structural screen","identifier":IDENT,"source_path":"release/hr-v0/j2-stop-pad-pocket-fea-p0.1/analysis-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - INTERNAL LINEAR SCREEN PASS / UNSELECTED","release_boundary":"nonlinear contact, joined hardware/frame, material allowable, dynamics, tolerance, physical correlation and qualified closure open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv",current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-56","prior_identifier":"HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1","current_or_required_successor":IDENT,"disposition":"superseded for current structural calculation because prior C06/C07 force directions were simplified and P0.13 pockets were absent","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv",supers)
    ch,ca = rows(CFG/"open-holds.csv"),rows(CFG/"acceptance-matrix.csv")
    for hold in holds:
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled analysis/physical result and qualified acceptance","warning":WARNING})
        ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"open-holds.csv",ch); write_csv(CFG/"acceptance-matrix.csv",ca)
    gates=rows(CFG/"gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005","EG-006","EG-007","EG-028"}:
            gate["evidence_added"] += f"; {IDENT} exact-normal P0.13 metal-perimeter/pocket-floor linear screens"
            gate["remaining_evidence"] += "; converged nonlinear contact/joined-load/dynamic/tolerance/physical correlation and qualified acceptance"
    write_csv(CFG/"gate-impact.csv",gates)
    cfg_status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R278","system_bom_groups":len(rows(ROOT/"bom/bom.csv")),"current_records":len(current),"supersession_records":len(supers),"open_holds":len(ch),"acceptance_rows":len(ca),"p013_fea_review":IDENT,"p013_fea_disposition":"PASSES INTERNAL EXACT-NORMAL LINEAR GEOMETRY SCREEN - UNSELECTED","prior_p012_fea_current_use_authorized":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG/"package-status.json").write_text(json.dumps(cfg_status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR278 indexes the corrected exact-normal P0.13 linear screens. P0.13 remains unselected; nonlinear, joined-load, dynamic, physical and qualified closure remains open.\n",encoding="utf-8")
    write_csv(CFG/"source-hash-register.csv",[{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(FEA/"index.html",CFG/"index.html"); manifest(CFG); shutil.copytree(CFG,CFG_REL); manifest(CFG_REL)

    (ROOT/"docs/hr-v0-j2-stop-pad-pocket-fea-p0.1.md").write_text(f"# HR-V0 J2 stop P0.13 exact-normal linear screen\n\n> **{WARNING}**\n\nR278 issues `{IDENT}` and supersedes the P0.12 linear result for current structural calculation. The exact CAD normal transforms to `[0, 0, -1]` in C06 local coordinates; C07 receives the equal-and-opposite fixed-frame vector `[0, -0.882948, -0.469470]`.\n\nAt the finest 2 mm global mesh, the nominal single-rail 253.607 N screens give {c06['finest_global_maximum_mpa']:.3f} MPa for C06, {perimeter['finest_global_maximum_mpa']:.3f} MPa for the pad-absent C07 metal perimeter, and {floor['finest_global_maximum_mpa']:.3f} MPa for the C07 pocket floor. The minimum arithmetic ratio to the 240 MPa project MTR threshold is {min(c06['ratio_to_project_threshold'],perimeter['ratio_to_project_threshold'],floor['ratio_to_project_threshold']):.3f}. These pass the internal geometry-rejection rule only.\n\nThe solver is linear elastic with ideal fixed-hole restraints and distributed loads. It does not prove local contact, bolt/frame/extrusion capacity, accepted material allowables, impact, fatigue, tolerances or physical correlation. P0.13 remains unselected.\n\n[Interactive analysis](../release/hr-v0/j2-stop-pad-pocket-fea-p0.1/index.html)\n",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r278-calculation-correction.md").write_text(f"# R278 J2 stop calculation correction\n\n> **{WARNING}**\n\nThe current P0.12 linear C06/C07 result is superseded for calculation use. Its C06 vector was a trigonometric approximation not obtained by transforming the exact B-Rep normal, and its C07 load omitted the exact Z component. It also predated the P0.13 pad pockets. R278 binds the exact force pair and separate P0.13 load surfaces. Historical artifacts remain for traceability and receive no current release credit.\n",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r278-independent-review-request.md").write_text(f"# R278 independent review request\n\n> **{WARNING}**\n\nPlease independently review `{IDENT}` for coordinate-transform/sign correctness, equal-and-opposite force balance, P0.13 boundary selection, mesh quality/sensitivity, stress/displacement arithmetic, material-threshold wording, omitted nonlinear/joined/dynamic physics, configuration supersession and fail-closed authority. No geometry or analysis is released.\n",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r278-status.md").write_text(f"# Sol R12 post-R278 status\n\n> **{WARNING}**\n\nR278 corrects the nominal P0.13 stop load direction and screens pad-absent and pocket-floor paths. It closes no Sol blocker: the result is linear and unqualified; exact hardware, nonlinear contact/joined load, dynamics, stopping, physical correlation, functional-safety allocation and authority remain open.\n",encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md"; old=handoff.read_text(encoding="utf-8")
    if not old.startswith("R278 exact-normal J2 stop correction:"):
        handoff.write_text(f"R278 exact-normal J2 stop correction: **`{IDENT}` supersedes the P0.12 result for current calculation, corrects both part-coordinate force vectors, and separately screens P0.13 metal-perimeter and pocket-floor transfer. All nominal linear cases pass the internal geometry screen, but P0.13 remains unselected and every nonlinear, joined-load, dynamic, physical and qualified gate remains open.**\n\n"+old,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; text=ledger.read_text(encoding="utf-8").replace("Two hundred seventy-seven rounds are complete (R01-R277).","Two hundred seventy-eight rounds are complete (R01-R278).")
    if "| R278 |" not in text:
        text=text.rstrip()+f"\n| R278 | 2026-08-12 | Exact-normal P0.13 stop structural correction | Codex project-owned calculation/configuration correction; not independent or qualified review | P0.12 C06 used a non-exact transformed direction, C07 omitted the exact Z component, and neither represented P0.13 pockets. | Issued exact equal/opposite part-frame loads and separate C07 metal-perimeter/pocket-floor linear screens. All pass only the internal geometry filter; P0.12 result is superseded for current calculation and all nonlinear/joined/dynamic/material/physical/qualified holds remain. | `docs/hr-v0-j2-stop-pad-pocket-fea-p0.1.md`; `release/hr-v0/j2-stop-pad-pocket-fea-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.42/` |\n"
    ledger.write_text(text,encoding="utf-8")
    readme=ROOT/"README.md"; text=readme.read_text(encoding="utf-8"); marker="## Start here\n\n"; links="- [R278 exact-normal P0.13 stop analysis](docs/hr-v0-j2-stop-pad-pocket-fea-p0.1.md)\n- [R278 calculation correction](docs/reviews/2026-08-12-r278-calculation-correction.md)\n- [R278 independent review request](docs/reviews/2026-08-12-r278-independent-review-request.md)\n- [R278 validation record](docs/reviews/2026-08-12-r278-validation-record.md)\n- [Interactive R278 structural guide](release/hr-v0/j2-stop-pad-pocket-fea-p0.1/index.html)\n- [Interactive configuration reconciliation P0.42](release/hr-v0/configuration-reconciliation-p0.42/index.html)\n"
    if links.splitlines()[0] not in text: text=text.replace(marker,marker+links)
    text=text.replace("Two hundred seventy-seven rounds are complete: R01-R277.","Two hundred seventy-eight rounds are complete: R01-R278.")
    readme.write_text(text,encoding="utf-8")
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print(f"Generated R278 {IDENT} and {CFG_IDENT}; no work authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
