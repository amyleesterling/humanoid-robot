#!/usr/bin/env python3
"""Generate R277 J2 bonded-pad-pocket integration package P0.1."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
PKG = ROOT / "mechanical/stops/hr-v0-j2-pad-pocket-p0.1"
REL = ROOT / "release/hr-v0/j2-pad-pocket-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.40"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.41"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.41"
IDENT = "HR-V0-J2-PAD-POCKET-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.41"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    records = [{"relative_path":p.relative_to(directory).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING}
               for p in sorted(directory.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, object]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{html.escape(field.replace('_',' '))}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(record.get(field,'')))}</td>" for field in fields) + "</tr>" for record in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    for target in (PKG, REL, CFG, CFG_REL):
        if target.exists():
            shutil.rmtree(target)
    PKG.mkdir(parents=True)

    definition = rows(CAD / "j2-pad-pocket-definition.csv")
    tolerance = rows(CAD / "j2-pad-pocket-tolerance-screen.csv")
    inspection = rows(CAD / "j2-pad-pocket-inspection.csv")
    cad_status = json.loads((CAD / "p013-status.json").read_text(encoding="utf-8"))
    candidates = [
        {"item":"soft contact coupon","manufacturer":"Rogers Corporation","identity":"2300327 / PORON 4790-92-25024-04P","geometry":"40.0 x 12.0 mm, R1.5 finished coupon; 0.61 +/-0.08 mm published stock thickness","role":"sacrificial noise/rebound contact layer only","selection_state":"EXACT MATERIAL CANDIDATE HOLD - CONVERTER/CUT ORDER, LOT AND QUALIFICATION OPEN","warning":WARNING},
        {"item":"retention film","manufacturer":"3M","identity":"467MP / 200MP adhesive transfer tape","geometry":"converter-laminated to the Rogers PET-supported face; 2.3 mil / 0.06 mm typical tape thickness, not a released tolerance","role":"nonstructural retention only; loss must leave metal backup available","selection_state":"EXACT PRODUCT-FAMILY CANDIDATE HOLD - ROLL CONFIGURATION/CONVERTER/APPLICATION QUALIFICATION OPEN","warning":WARNING},
        {"item":"pocketed fixed catch","manufacturer":"Project Button","identity":"MV0-C07 P0.13","geometry":"two 12.4 x 40.4 mm R2 pockets at X +/-44, Z 1; nominal CAD depth 0.52 mm","role":"locates bonded coupons and preserves surrounding structural metal stop","selection_state":"UNSELECTED CAD CANDIDATE - DEPENDENT DEPTH/DFM/FAI/STRUCTURAL/PHYSICAL REVIEW OPEN","warning":WARNING},
    ]
    write_csv(PKG / "candidate-definition.csv", candidates)
    write_csv(PKG / "pocket-definition.csv", definition)
    write_csv(PKG / "tolerance-screen.csv", tolerance)
    write_csv(PKG / "inspection-plan.csv", inspection)

    sources = [
        {"source_id":"POCKET-SRC-001","manufacturer":"Rogers Corporation","document":"PORON 4790-92-25024-P Extra Soft Slow Rebound Supported data sheet, publication 17-085, revision 1224-PDF","official_url":"https://rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/data-sheets/17-085-poron-4790-92-25024-p-extra-soft---slow-rebound---supported.pdf","revision_or_date":"1224-PDF / 2024; accessed 2026-08-12","verified_use":"2300327 family material; 0.61 +/-0.08 mm; PET supported; CFD/compression-set/temperature boundaries","excluded_use":"finished coupon order, adhesive compatibility, impact rating, life or structural stop","warning":WARNING},
        {"source_id":"POCKET-SRC-002","manufacturer":"Rogers Corporation","document":"PORON Polyurethanes Product Availability Brochure 17-082","official_url":"https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/product-availability/17-082-poron-polyurethanes-product-availability-brochure.pdf","revision_or_date":"current manufacturer brochure; accessed 2026-08-12","verified_use":"product number 2300327 and stock family identity","excluded_use":"current purchasability, converter or cut-piece order","warning":WARNING},
        {"source_id":"POCKET-SRC-003","manufacturer":"3M","document":"3M Adhesive Transfer Tape 467MP Technical Data Sheet","official_url":"https://multimedia.3m.com/mws/media/2366204O/3M-Adhesive-Transfer-Tape-467MP.pdf?pif=000024","revision_or_date":"September 2024; supersedes June 2024; accessed 2026-08-12","verified_use":"467MP identity; 200MP adhesive; metal/high-surface-energy plastic application; 2.3 mil / 0.06 mm typical thickness","excluded_use":"specification tolerance, PORON application approval, exact roll/converter code, durability or safety function","warning":WARNING},
        {"source_id":"POCKET-SRC-004","manufacturer":"Project Button","document":"P0.13 controlled CAD status and exact pocket B-Rep","official_url":"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/p013-status.json","revision_or_date":"R277 / 2026-08-12","verified_use":f"status SHA-256 {sha(CAD/'p013-status.json')}; exact pocketed C07 and nominal pad-screen geometry","excluded_use":"as-built part, received stack, FAI, physical validation or fabrication release","warning":WARNING},
    ]
    write_csv(PKG / "source-register.csv", sources)

    stack = [
        {"stack_id":"STACK-01","term":"received laminated pad plus adhesive stack t_stack","value":"MEASURE EACH RECEIVED COUPON; no drawing nominal substitutes","tolerance_or_uncertainty":"gage force/anvil/repeatability and within-coupon map SELECTION REQUIRED","equation":"input to dependent feature","result":"OPEN","warning":WARNING},
        {"stack_id":"STACK-02","term":"finished pocket depth d_pocket","value":"t_stack - 0.150 mm","tolerance_or_uncertainty":"machining and metrology allocation SELECTION REQUIRED","equation":"dependent depth","result":"OPEN - DO NOT MACHINE FROM 0.520 MM CAD SCREEN","warning":WARNING},
        {"stack_id":"STACK-03","term":"installed protrusion p","value":"0.100..0.200 mm candidate acceptance band","tolerance_or_uncertainty":"directly inspect four corners/coupon after lamination","equation":"p=t_installed-d_as_built","result":"QUALIFIED ACCEPTANCE REQUIRED","warning":WARNING},
        {"stack_id":"STACK-04","term":"metal backup travel","value":"equal to measured local installed protrusion only after first contact","tolerance_or_uncertainty":"compression/contact/deformation and first-contact sharing unresolved","equation":"not the historical 0.750 mm envelope","result":"PHYSICAL DYNAMIC CLOSURE REQUIRED","warning":WARNING},
    ]
    write_csv(PKG / "dependent-depth-stack.csv", stack)

    failures = [
        {"failure_id":"PAD-FM-01","failure":"pad or adhesive absent/detached","required_behavior":"surrounding P0.13 metal face remains available as structural stop; earlier/noisier contact allowed","evidence":"coupon-loss static/contact and guarded physical test","state":"OPEN","warning":WARNING},
        {"failure_id":"PAD-FM-02","failure":"pad bottoms out","required_behavior":"load transfers to continuous metal perimeter without pad structural credit","evidence":"contact witness, force/angle/current trace and nonlinear joined model","state":"OPEN","warning":WARNING},
        {"failure_id":"PAD-FM-03","failure":"one coupon thicker or contacts first","required_behavior":"single-rail load case governs; no equal-sharing credit","evidence":"worst-tolerance analysis plus single-rail physical proof","state":"OPEN","warning":WARNING},
        {"failure_id":"PAD-FM-04","failure":"adhesive creep/migration or contamination","required_behavior":"no loose fragment creates jam; inspection/replacement interval catches degradation","evidence":"aging, temperature, contamination and cycle-life test","state":"OPEN","warning":WARNING},
        {"failure_id":"PAD-FM-05","failure":"pocket depth made from nominal CAD rather than received stack","required_behavior":"traveler blocks installation and motion; part quarantined","evidence":"lot-specific depth calculation, FAI and configuration signature","state":"OPEN","warning":WARNING},
    ]
    write_csv(PKG / "failure-mode-register.csv", failures)

    holds_text = [
        "Current converter quote binds Rogers 2300327, 3M 467MP, PET-side lamination, 40 x 12 mm R1.5 coupons, tolerances, lot traceability and CoC",
        "3M/Rogers or qualified materials reviewer accepts the aluminum-467MP-PET/PORON application and surface-preparation process",
        "Received laminated-stack thickness is mapped with a qualified low-force method and dependent pocket depth is released lot-by-lot",
        "Machine supplier accepts R2 pocket DFM and reports as-built plan/depth/finish without using 0.520 mm as production depth",
        "Installed protrusion candidate band 0.100..0.200 mm is accepted against stopping, guard, pinch and contact requirements",
        "First article passes pocket, protrusion, retention and continuous metal-backup inspections",
        "Pad-absent, one-pad, bottom-out, rebound, migration and jam fault tests pass defined limits",
        "Dynamic force-stroke, current/torque decay, stopping time/angle and energy integration pass at accepted approach/fault speeds",
        "P0.13 C06/C07 full joined load path and local pocket/contact stresses pass qualified nonlinear analysis and physical correlation",
        "Qualified release and separate procurement, machining, assembly and powered-work authorizations are signed",
    ]
    holds = [{"hold_id":f"R277-H{i:02d}","hold":text,"state":"OPEN","execution":"NOT EXECUTED","release_effect":"BLOCKS PAD-POCKET SELECTION/FABRICATION/MOTION","warning":WARNING} for i,text in enumerate(holds_text,1)]
    write_csv(PKG / "open-holds.csv", holds)
    write_csv(PKG / "acceptance-matrix.csv", [{"acceptance_id":f"R277-ACC-{i:02d}","criterion":text,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,text in enumerate(holds_text,1)])

    tests = [
        {"test_id":"PADP-T-01","test":"incoming stack thickness map","configuration":"both coupons, five points each, qualified low-force gage","acceptance":"lot-specific limits and uncertainty SELECTION REQUIRED","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-02","test":"pocket and installed protrusion FAI","configuration":"both pockets and four corners per installed coupon","acceptance":"dependent depth record plus every protrusion 0.100..0.200 mm after qualified approval","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-03","test":"retention peel/migration screen","configuration":"surface preparation, dwell, temperature and force protocol SELECTION REQUIRED","acceptance":"numerical force/migration limit SELECTION REQUIRED","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-04","test":"pad-absent metal-backup proof","configuration":"guarded unpowered/low-energy sequence defined by qualified reviewer","acceptance":"metal contact occurs without jam or loss of stop path","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-05","test":"single-pad first-contact and bottom-out","configuration":"worst side and tolerance; synchronized force/current/angle","acceptance":"limits SELECTION REQUIRED; no equal-share credit","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-06","test":"two-pad nominal stopping transient","configuration":"accepted max normal/fault speed and received stack","acceptance":"force, energy, angle, time, rebound and temperature limits SELECTION REQUIRED","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-07","test":"temperature/contamination/cycle-life sequence","configuration":"accepted environmental and duty-cycle envelope","acceptance":"retention, protrusion, rebound and wear limits SELECTION REQUIRED","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"test_id":"PADP-T-08","test":"post-test metal-backup/contact inspection","configuration":"dye/contact transfer plus dimensional and crack inspection","acceptance":"continuous intended witness and no unacceptable damage; limits/method SELECTION REQUIRED","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
    ]
    write_csv(PKG / "verification-matrix.csv", tests)

    status = {"identifier":IDENT,"round":"R277","date":"2026-08-12","cad_identifier":cad_status["identifier"],
              "pad_candidate":"Rogers 2300327","retention_candidate":"3M 467MP","coupon_count":2,
              "coupon_nominal_mm":[40.0,12.0,0.61],"cad_screen_pocket_depth_mm":0.52,
              "production_depth":"DEPENDENT - RECEIVED LAMINATED STACK MINUS 0.150 MM",
              "installed_protrusion_candidate_band_mm":[0.1,0.2],"metal_backup_preserved":True,
              "pad_structural_credit":False,"candidate_selected":False,"physical_evidence_complete":False,
              "qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,
              "assembly_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,
              "energization_authorized":False,"safety_credit":False,"open_holds":len(holds),"warning":WARNING}
    (PKG / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (PKG / "README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR277 adds exact P0.13 bonded-pad pockets and a received-stack-dependent machining rule. The 0.520 mm CAD depth is visualization only. Rogers 2300327 and 3M 467MP remain unselected candidates; the pad receives zero structural credit and the surrounding metal stop remains mandatory.\n",encoding="utf-8")

    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R277 J2 pad-pocket candidate</title><script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js'></script><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--paper:#f7fbff;--line:#9ccfe8;--red:#9b1c1c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1200px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(26px,3vw,40px);line-height:1.18;color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}}.card,.decision{{background:white;border:2px solid var(--line);border-radius:15px;padding:20px}}.card strong{{display:block;font-size:34px;color:var(--navy)}}.decision{{border-left:10px solid var(--gold)}}.viewer{{border:3px solid var(--navy);border-radius:16px;overflow:hidden;background:var(--pale)}}model-viewer{{display:block;width:100%;height:clamp(470px,70vh,720px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p{{padding:14px 18px;background:white;margin:0}}.diagram{{width:100%;height:auto;background:white;border:2px solid var(--line);border-radius:14px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}label{{font-weight:850;display:block;margin:12px 0}}input{{font:16px system-ui;padding:8px;width:180px}}output{{font-size:24px;font-weight:900;color:var(--navy)}}.bad{{color:var(--red);font-weight:850}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}model-viewer{{height:480px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R277 &middot; {IDENT} &middot; dimensioned geometry, zero release</p><h1>The J2 contact pad now has a real place to live.</h1><p>Two rounded pockets locate bonded coupons while a continuous metal perimeter remains the structural stop.</p></div></header><main><section class='grid'><div class='card'><strong>2</strong>pad pockets</div><div class='card'><strong>40 × 12 mm</strong>finished coupons</div><div class='card'><strong>0.10–0.20 mm</strong>candidate installed protrusion</div><div class='card'><strong>0</strong>pad structural credit; zero structural credit claimed</div></section><section class='decision'><h2>Do not machine the 0.520 mm screen depth</h2><p>The final pocket depth is a dependent feature: measure each complete received pad-plus-adhesive stack, then set <strong>d<sub>pocket</sub> = t<sub>stack</sub> − 0.150 mm</strong>. Directly inspect the installed protrusion. The candidate 0.10–0.20 mm acceptance band still needs qualified approval.</p></section><section><h2>Orbit the pocketed catch and nominal pads</h2><div class='viewer'><model-viewer src='../../../cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/HR-V0_J2_C07_pad-pocket-installed-screen.glb' alt='Interactive 3D model of the P0.13 fixed catch with two nominal soft contact pads' camera-controls camera-orbit='35deg 70deg 90%' min-camera-orbit='auto auto 30%' max-camera-orbit='auto auto 320%' field-of-view='28deg' shadow-intensity='.8'></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Yellow pads are nominal visualization solids, not released parts.</p></div></section><section><h2>Front-face geometry</h2><svg class='diagram' viewBox='0 0 1000 520' role='img' aria-label='Dimensioned front view of the twin pad pockets'><rect x='90' y='60' width='820' height='390' rx='16' fill='#e4f6ff' stroke='#082b55' stroke-width='5'/><rect x='142' y='80' width='124' height='370' rx='20' fill='#f4b942' stroke='#082b55' stroke-width='4'/><rect x='734' y='80' width='124' height='370' rx='20' fill='#f4b942' stroke='#082b55' stroke-width='4'/><text x='500' y='115' font-size='28' text-anchor='middle' fill='#082b55' font-weight='800'>MV0-C07 contact side</text><text x='204' y='275' font-size='24' text-anchor='middle' fill='#082b55' transform='rotate(-90 204 275)'>12.4 × 40.4 pocket</text><text x='796' y='275' font-size='24' text-anchor='middle' fill='#082b55' transform='rotate(90 796 275)'>12.4 × 40.4 pocket</text><text x='500' y='390' font-size='23' text-anchor='middle' fill='#082b55'>centers X = ±44.000 mm · Z = 1.000 mm · corner R2.0</text><text x='500' y='425' font-size='22' text-anchor='middle' fill='#9b1c1c' font-weight='800'>white/blue perimeter is the structural metal backup</text></svg></section><section class='card'><h2>Dependent-depth calculator</h2><p>Enter the measured complete laminated stack. This calculator applies the candidate 0.150 mm target; it is not machining authorization.</p><label>Measured stack thickness, mm <input id='stack' type='number' min='.1' max='2' step='.001' value='.668'></label><p><output id='depth'>candidate pocket depth 0.518 mm</output></p></section><section><h2>Dependent stack</h2>{table(stack)}</section><section><h2>Failure behavior</h2>{table(failures)}</section><section><h2>Open release holds</h2>{table(holds)}</section></main><script>const i=document.getElementById('stack'),o=document.getElementById('depth');function u(){{const v=Number(i.value);o.value=Number.isFinite(v)?'candidate pocket depth '+(v-.15).toFixed(3)+' mm':'enter a measured stack'}}i.addEventListener('input',u);u();</script></body></html>"""
    (PKG / "index.html").write_text(page,encoding="utf-8")
    manifest(PKG)
    shutil.copytree(PKG, REL)
    manifest(REL)

    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-60","role":"P0.13 bonded-pad-pocket geometry and received-stack-dependent depth control","identifier":IDENT,"source_path":"release/hr-v0/j2-pad-pocket-p0.1/package-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - P0.13/PAD/ADHESIVE UNSELECTED","release_boundary":"CAD screen depth is not production depth; supplier, stack, DFM, FAI, dynamics, structure, physical and qualified closure open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-55","prior_identifier":"HR-V0-CONFIG-REC-P0.40","current_or_required_successor":CFG_IDENT,"disposition":"superseded for indexing; R277 adds P0.13 pockets/dependent depth without selecting or releasing P0.13, pad or adhesive","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    ch, ca = rows(CFG / "open-holds.csv"), rows(CFG / "acceptance-matrix.csv")
    for hold in holds:
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled physical result and qualified acceptance","warning":WARNING})
        ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "open-holds.csv", ch); write_csv(CFG / "acceptance-matrix.csv", ca)
    bmap = rows(CFG / "bom-integration-map.csv")
    for row in bmap:
        if row["item_id"] == "BOM-110":
            row.update({"role":"two 40 x 12 mm Rogers 2300327 coupons, converter laminated and cut","bound_identifier":IDENT,"closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO"})
    bmap.append({"item_id":"BOM-111","role":"3M 467MP nonstructural pad-retention transfer adhesive; exact roll/converter configuration","bound_identifier":IDENT,"closure_class":"exact_product_family_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO","warning":WARNING})
    write_csv(CFG / "bom-integration-map.csv", bmap)
    gates = rows(CFG / "gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005","EG-006","EG-007","EG-028"}:
            gate["evidence_added"] += f"; {IDENT} exact pocket plan, dependent-depth rule, retention failure boundary and inspection route"
            gate["remaining_evidence"] += "; received laminated stack, qualified protrusion band, P0.13 structure/DFM/FAI and guarded physical dynamics"
    write_csv(CFG / "gate-impact.csv", gates)
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R277","current_records":len(current),"supersession_records":len(supers),"bom_integration_records":len(bmap),"open_holds":len(ch),"acceptance_rows":len(ca),"p013_candidate":cad_status["identifier"],"j2_pad_pocket_review":IDENT,"j2_pad_selected":False,"j2_retention_selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG / "package-status.json").write_text(json.dumps(cfg_status,indent=2)+"\n",encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR277 indexes the P0.13 pad-pocket geometry and dependent-depth control. The 0.520 mm CAD depth is not a machining dimension; pad, adhesive and P0.13 remain unselected.\n",encoding="utf-8")
    write_csv(CFG / "source-hash-register.csv", [{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(PKG / "index.html", CFG / "index.html")
    manifest(CFG); shutil.copytree(CFG, CFG_REL); manifest(CFG_REL)

    bom_path = ROOT / "bom/bom.csv"; bom = rows(bom_path)
    for row in bom:
        if row["item_id"] == "BOM-110":
            row.update({"quantity":"2 finished 40 x 12 mm R1.5 coupons from one quoted converter route","selection_basis":f"R277 exact material candidate for sacrificial contact/noise/rebound only; converter laminates retention film to PET-supported face and cuts coupons. Quote, lot/CoC, stack map, dependent pocket depth, retention/dynamics/life/physical proof and qualified acceptance open. {WARNING}"})
    if not any(r["item_id"] == "BOM-111" for r in bom):
        bom.append({"item_id":"BOM-111","subsystem":"j2_soft_contact_pad_retention","manufacturer":"3M","manufacturer_part_number":"467MP / Adhesive 200MP; exact roll size and converter-laminated cut-piece order SELECTION REQUIRED","quantity":"2 finished 40 x 12 mm adhesive films applied by selected converter","baseline_status":"exact_product_family_candidate_hold","selection_basis":f"R277 nonstructural retention candidate only. September 2024 TDS gives 2.3 mil/0.06 mm typical thickness and metal/HSE-plastic application; not a specification tolerance or PORON application approval. Quote, converter, surface prep, lot/CoC, stack measurement, peel/migration/life proof and qualified acceptance open. {WARNING}"})
    write_csv(bom_path,bom)

    doc = ROOT / "docs/hr-v0-j2-pad-pocket-p0.1.md"
    doc.write_text(f"# HR-V0 J2 pad-pocket P0.1\n\n> **{WARNING}**\n\nR277 issues P0.13 with two rounded 12.4 x 40.4 mm pockets for 40 x 12 mm Rogers 2300327 coupons. The surrounding P0.12 metal contact face is preserved as the structural backup. The pad and 3M 467MP retention film receive zero structural or safety credit.\n\nThe 0.520 mm CAD pocket depth is a visualization/DFM screen, not a machining dimension. Production depth is dependent on the measured complete received laminated stack: `d_pocket = t_stack - 0.150 mm`. The 0.100..0.200 mm installed protrusion band is a project candidate requiring qualified acceptance and direct first-article inspection.\n\n[Interactive pad-pocket guide](../release/hr-v0/j2-pad-pocket-p0.1/index.html)\n",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r277-independent-review-request.md").write_text(f"# R277 independent review request\n\n> **{WARNING}**\n\nPlease independently review `{IDENT}` and `{cad_status['identifier']}` for pocket geometry/DFM, continuous metal backup, dependent-depth control, Rogers/3M source interpretation, retention failure behavior, tolerance and inspection completeness, structural/dynamic test scope, BOM/configuration synchronization and fail-closed authority. The CAD screen depth is not a fabrication dimension and no candidate is selected.\n",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r277-status.md").write_text(f"# Sol R12 post-R277 status\n\n> **{WARNING}**\n\nR277 addresses a portion of Sol's missing build definition by adding exact soft-contact pocket geometry, a lot-dependent depth rule, a retention candidate, FAI and fault tests. It closes no Sol blocker: native build drawings, qualified structure/dynamics, received selections, physical evidence, safety allocation and work authorization remain open.\n",encoding="utf-8")
    handoff = ROOT / "docs/handoff-current.md"; old = handoff.read_text(encoding="utf-8")
    if not old.startswith("R277 J2 pad-pocket correction:"):
        handoff.write_text(f"R277 J2 pad-pocket correction: **`{IDENT}` adds two exact P0.13 pockets and a received-stack-dependent depth rule. The CAD 0.520 mm depth is not a machining instruction. Rogers 2300327, 3M 467MP and P0.13 remain unselected; metal backup is preserved; ten package holds remain open and zero work/safety authority exists.**\n\n" + old,encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"; text = ledger.read_text(encoding="utf-8").replace("Two hundred seventy-six rounds are complete (R01-R276).","Two hundred seventy-seven rounds are complete (R01-R277).")
    if "| R277 |" not in text:
        text = text.rstrip()+f"\n| R277 | 2026-08-12 | Dimensioned J2 pad-pocket and dependent-depth correction | Codex project-owned CAD/mechanical/configuration correction; not independent or qualified review | R276 left coupon plan, pocket, retention and installed backup gap undefined. | Issued P0.13 with two exact 12.4 x 40.4 mm R2 pockets, 40 x 12 mm R1.5 coupons, received-stack-dependent depth and 0.100..0.200 mm candidate protrusion inspection. Added held 3M 467MP retention, BOM-111, pad-loss/bottom-out faults, FAI and P0.41. CAD 0.520 mm depth is not a machining instruction; all selection/physical/qualified holds remain. | `docs/hr-v0-j2-pad-pocket-p0.1.md`; `cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/`; `release/hr-v0/j2-pad-pocket-p0.1/` |\n"
    ledger.write_text(text,encoding="utf-8")
    readme = ROOT / "README.md"; text = readme.read_text(encoding="utf-8")
    marker = "## Start here\n\n"; links = "- [R277 dimensioned J2 pad-pocket candidate](docs/hr-v0-j2-pad-pocket-p0.1.md)\n- [R277 independent review request](docs/reviews/2026-08-12-r277-independent-review-request.md)\n- [R277 validation record](docs/reviews/2026-08-12-r277-validation-record.md)\n- [Interactive R277 pad-pocket guide](release/hr-v0/j2-pad-pocket-p0.1/index.html)\n- [Interactive configuration reconciliation P0.41](release/hr-v0/configuration-reconciliation-p0.41/index.html)\n"
    if links.splitlines()[0] not in text: text = text.replace(marker,marker+links)
    text = text.replace("Two hundred seventy-six rounds are complete: R01-R276.","Two hundred seventy-seven rounds are complete: R01-R277.")
    text = text.replace("R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad; R276 supersedes its radius-based warning with P0.12's exact contact normal and retains the metal rails as the structural backup.","R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad; R276 supersedes its radius-based warning with P0.12's exact contact normal; R277 adds exact P0.13 pockets, a held 3M 467MP retention candidate and a received-stack-dependent depth while retaining the metal rails as structural backup.")
    readme.write_text(text,encoding="utf-8")

    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print(f"Generated R277 {IDENT} and {CFG_IDENT}; all selection, fabrication, physical and qualified gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
