#!/usr/bin/env python3
"""Generate R279 exact local-convergence protocol for the P0.13 J2 stop.

R278's 4/3/2 mm uniform P1 meshes are audited, not promoted.  The output
defines the exact next analysis contract and keeps R278-H02 open until the
protocol is executed and independently accepted.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R278 = ROOT / "mechanical/analysis/hr-v0-j2-stop-pad-pocket-fea-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-refinement-protocol-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-refinement-protocol-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.42"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.43"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.43"
IDENT = "HR-V0-J2-STOP-REFINEMENT-PROTOCOL-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.43"
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
    fields=list(records[0]); head="".join(f"<th>{html.escape(k.replace('_',' '))}</th>" for k in fields)
    body="".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(k,'')))}</td>" for k in fields)+"</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def relative_change(current: float, previous: float) -> float:
    return abs(current-previous)/abs(current)


def main() -> int:
    for target in (OUT, REL, CFG, CFG_REL):
        if target.exists(): shutil.rmtree(target)
    OUT.mkdir(parents=True)
    r278 = rows(R278 / "mesh-convergence.csv")
    audit: list[dict[str, object]] = []
    metrics = (
        ("global maximum stress","global_maximum_element_von_mises_mpa_mesh_sensitive"),
        ("global p99 stress","global_p99_element_von_mises_mpa"),
        ("reported root maximum stress","root_maximum_element_von_mises_mpa_mesh_sensitive"),
        ("reported root p99 stress","root_p99_element_von_mises_mpa"),
        ("maximum displacement","maximum_displacement_mm"),
        ("strain energy","strain_energy_n_mm"),
    )
    for case_id in sorted({r["case_id"] for r in r278}):
        case=[r for r in r278 if r["case_id"]==case_id]
        previous,current=case[-2:]
        for label,key in metrics:
            delta=relative_change(float(current[key]),float(previous[key]))
            audit.append({"case_id":case_id,"metric":label,"3_mm_value":previous[key],"2_mm_value":current[key],"last_pair_relative_change":f"{delta:.6f}","diagnostic":"NOT STABLE" if delta>0.05 else "NUMERICALLY STABLE ONLY; NOT H02 CLOSURE","reason":"uniform P1 mesh; fixed-hole idealization; physical zone not fixed" if "displacement" not in label and "energy" not in label else "uniform P1 mesh and idealized restraints","warning":WARNING})

    zones = [
        {"zone_id":"C06-RR-PROFILE","part":"C06 +X rail","exact_definition":"solid within 3.0 mm Euclidean distance of actual modeled R2 rail/shoulder transition edge near X=35 Z=20; full solid Y extent","required_outputs":"volume-weighted mean/RMS/p95 stress; hotspot subzone","selection_method":"distance to exact B-Rep edge; centroid box prohibited","warning":WARNING},
        {"zone_id":"C06-RR-STEP","part":"C06 +X web","exact_definition":"solid within 3.0 mm of actual R2 thickness-step blend; X>=20; -20<=Z<=20","required_outputs":"volume-weighted mean/RMS/p95 stress","selection_method":"distance to exact B-Rep edge; separate from profile root","warning":WARNING},
        {"zone_id":"C06-GAUGE","part":"C06 +X load path","exact_definition":"exact-solid intersection with registered section Z=18.000 mm","required_outputs":"integrated force/moment components; membrane+bending section stress","selection_method":"exact section integration","warning":WARNING},
        {"zone_id":"C07-PE-STRAIGHTS/CORNERS","part":"C07 +X pocket","exact_definition":"1.000 mm solid band around exact rounded pocket perimeter; center X=44 Z=1; 12.400 x 40.400 R2; Y=7.005..8.525","required_outputs":"separate straight-edge and four-corner volume mean/RMS/p95 stress","selection_method":"exact B-Rep distance and named edge identity","warning":WARNING},
        {"zone_id":"C07-PF","part":"C07 +X pocket backing","exact_definition":"exact pocket plan inset 1.000 mm; Y=7.005..8.005; floor Y=8.005","required_outputs":"center/four registered floor-normal displacement probes; volume mean/RMS/p95 stress","selection_method":"exact inset geometry and fixed probes","warning":WARNING},
        {"zone_id":"C07-GAUGE","part":"C07 +X throat","exact_definition":"exact-solid intersection with registered section X=34.000 mm","required_outputs":"integrated force/moment components; membrane+bending section stress","selection_method":"exact section integration","warning":WARNING},
        {"zone_id":"H1-H4/E1-E2","part":"each hole separately","exact_definition":"H axes X=+/-16 Z=+/-8 r=1.35; E axes X=0 Z=+/-10 r=2.75; Y=0..9.525","required_outputs":"separate 1 mm end-rim singular zones; wall Y=1..8.525; ligament radial band r+1..r+3; fixed-offset gauges 0.25/0.50/1.00/2.00 mm","selection_method":"exact cylindrical B-Rep identity and physical offsets","warning":WARNING},
    ]
    mesh = [
        {"level":"L0","global_max_mm":2.00,"rail_root_max_mm":0.50,"pocket_max_mm":0.26,"hole_max_mm":0.40,"growth_max":1.4,"purpose":"initial local study","warning":WARNING},
        {"level":"L1","global_max_mm":1.40,"rail_root_max_mm":0.35,"pocket_max_mm":0.18,"hole_max_mm":0.28,"growth_max":1.4,"purpose":"refinement pair 1","warning":WARNING},
        {"level":"L2","global_max_mm":1.00,"rail_root_max_mm":0.25,"pocket_max_mm":0.13,"hole_max_mm":0.20,"growth_max":1.4,"purpose":">=4 elements through 0.520 mm pocket depth","warning":WARNING},
        {"level":"L3","global_max_mm":0.70,"rail_root_max_mm":0.18,"pocket_max_mm":0.09,"hole_max_mm":0.14,"growth_max":1.4,"purpose":"final planned level; add L4 if convergence invalid","warning":WARNING},
    ]
    criteria = [
        {"criterion_id":"R279-C01","metric":"geometry/source identity","acceptance":"same SHA-bound P0.13 STEP, material, load resultant/vector and BC at every level; P2 tetrahedra primary or independent P2 cross-check","fail_closed_rule":"any model drift fails protocol","warning":WARNING},
        {"criterion_id":"R279-C02","metric":"mesh quality","acceptance":"positive Jacobian; min SICN >=0.10; <=0.1% below 0.20; monitored zones min SICN >=0.20; full histogram recorded","fail_closed_rule":"any level failing quality fails protocol","warning":WARNING},
        {"criterion_id":"R279-C03","metric":"equilibrium","acceptance":"normalized force balance <=1e-8 and normalized moment balance about fixed datum <=1e-6","fail_closed_rule":"either balance failure fails protocol","warning":WARNING},
        {"criterion_id":"R279-C04","metric":"loaded surface","acceptance":"area <=0.25% from exact B-Rep and <=0.10% last pair; resultant/location/moment <=0.10%","fail_closed_rule":"surface/resultant drift fails protocol","warning":WARNING},
        {"criterion_id":"R279-C05","metric":"energy/displacement","acceptance":"strain energy and every fixed registered displacement probe <=2% last-pair change","fail_closed_rule":"any required probe failure leaves H02 open","warning":WARNING},
        {"criterion_id":"R279-C06","metric":"gauge sections","acceptance":"each integrated force/moment component <=1%; derived membrane+bending stress <=3%","fail_closed_rule":"any component failure leaves H02 open","warning":WARNING},
        {"criterion_id":"R279-C07","metric":"nonsingular stress zones","acceptance":"volume-weighted mean/RMS <=3% and p95 <=5% for both L1->L2 and L2->L3; hotspot stays in same named subzone","fail_closed_rule":"no global/element-count percentile substitution","warning":WARNING},
        {"criterion_id":"R279-C08","metric":"GCI/order","acceptance":"three finest levels; positive plausible order; asymptotic ratio 0.8..1.25; GCI95 <=5% for every decision metric","fail_closed_rule":"oscillatory/invalid order requires L4 and keeps H02 open","warning":WARNING},
        {"criterion_id":"R279-C09","metric":"singular rims/contact lines","acceptance":"raw maximum versus h reported separately; no convergence or 240 MPa comparison claimed","fail_closed_rule":"concealment/averaging/capacity use fails protocol","warning":WARNING},
        {"criterion_id":"R279-C10","metric":"scope of closure","acceptance":"at most numerical convergence of idealized R278 model; H03/H04/physical/qualified gates stay open","fail_closed_rule":"no selection, capacity, fabrication, motion or energization credit","warning":WARNING},
    ]
    singularity = [
        {"zone":"each H1-H4/E1-E2 end rim","required_report":"raw maximum and maximum-versus-local-h at each end separately","interpretation":"EXPECTED/UNRESOLVED IDEALIZATION if peak grows","capacity_use":"PROHIBITED","warning":WARNING},
        {"zone":"any load-edge/contact-line singularity","required_report":"raw maximum and maximum-versus-local-h; identify exact B-Rep edge","interpretation":"UNRESOLVED CONTACT IDEALIZATION","capacity_use":"PROHIBITED","warning":WARNING},
        {"zone":"0.25/0.50/1.00/2.00 mm fixed rim offsets","required_report":"fixed-volume weighted metrics and BC sensitivity","interpretation":"diagnostic only even if converged","capacity_use":"PROHIBITED until H04/physical correlation","warning":WARNING},
    ]
    for name,data in (("r278-instability-audit.csv",audit),("physical-zone-register.csv",zones),("mesh-plan.csv",mesh),("acceptance-criteria.csv",criteria),("singularity-register.csv",singularity)):
        write_csv(OUT/name,data)
    holds=[
        "Execute the four-level curvature-conforming local mesh study with exact B-Rep zone identities and complete raw solver evidence",
        "Run/accept a P2 primary study or independent P2 cross-check and report quality histograms, section resultants, GCI and singularity trends",
        "Qualified reviewer accepts the protocol, its execution and only numerical convergence of the idealized R278 model",
        "H03 nonlinear contact, H04 joined hardware/frame, physical correlation and qualified capacity remain separately open",
    ]
    write_csv(OUT/"open-holds.csv",[{"hold_id":f"R279-H{i:02d}","hold":h,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS R278-H02 AND P0.13 SELECTION/FABRICATION/MOTION","warning":WARNING} for i,h in enumerate(holds,1)])
    write_csv(OUT/"acceptance-matrix.csv",[{"acceptance_id":f"R279-ACC-{i:02d}","criterion":h,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,h in enumerate(holds,1)])
    status={"identifier":IDENT,"round":"R279","date":"2026-08-12","cad_identifier":"HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE","r278_analysis":"HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1","r278_metrics_audited":len(audit),"r278_metrics_over_5_percent":sum(float(r["last_pair_relative_change"])>0.05 for r in audit),"protocol_zones":len(zones),"mesh_levels":len(mesh),"acceptance_criteria":len(criteria),"mesh_refinement_hold_closed":False,"execution_complete":False,"disposition":"R278-H02 OPEN - current uniform P1 study is not local convergence evidence; exact executable successor protocol issued","selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR279 audits the R278 uniform P1 mesh and issues the exact local-convergence protocol. It does not execute or close R278-H02.\n",encoding="utf-8")
    page=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R279 J2 convergence protocol</title><style>:root{{--navy:#082b55;--deep:#041a35;--sky:#7dd3fc;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8;--red:#9b1c1c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05}}h2{{font-size:clamp(26px,3vw,40px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:900}}.truth,.decision{{background:white;border:2px solid var(--line);border-left:10px solid var(--gold);border-radius:15px;padding:20px;margin:22px 0}}.decision{{border-left-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R279 &middot; {IDENT}</p><h1>A coarse mesh is not convergence.</h1><p>R279 exposes the unstable R278 outputs and defines the exact local, singularity-aware study required next.</p></div></header><main><section class='decision'><h2>R278-H02 remains open</h2><p><strong>{status['r278_metrics_over_5_percent']} of {status['r278_metrics_audited']}</strong> audited last-pair metrics change by more than 5%. The 2 mm global P1 mesh cannot resolve the 0.520 mm pocket step. Fixed-hole peaks are reported as unresolved idealization effects, never compared to capacity.</p></section><section><h2>R278 instability audit</h2>{table(audit)}</section><section><h2>Exact physical zones</h2>{table(zones)}</section><section><h2>Four-level mesh plan</h2>{table(mesh)}</section><section><h2>Fail-closed acceptance</h2>{table(criteria)}</section><section><h2>Singularity disclosure</h2>{table(singularity)}</section><section><h2>Open holds</h2>{table(rows(OUT/'open-holds.csv'))}</section><section class='truth'><h2>What a future pass could mean</h2><p>Only numerical convergence of the idealized R278 model. Nonlinear contact, the actual bolted/frame joint, material allowables, dynamics, physical correlation and qualified acceptance remain separate blockers.</p></section></main></body></html>"""
    (OUT/"index.html").write_text(page,encoding="utf-8")
    manifest(OUT); shutil.copytree(OUT,REL); manifest(REL)

    shutil.copytree(CFG0,CFG)
    current=rows(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-62","role":"P0.13 J2 stop exact local mesh-convergence execution protocol","identifier":IDENT,"source_path":"release/hr-v0/j2-stop-refinement-protocol-p0.1/analysis-status.json","configuration_state":"CURRENT REVIEW PROTOCOL - NOT EXECUTED / H02 OPEN","release_boundary":"P2/local mesh execution, qualified numerical acceptance, H03/H04/dynamics/physical correlation remain open","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",current)
    ch,ca=rows(CFG/"open-holds.csv"),rows(CFG/"acceptance-matrix.csv")
    for hold in rows(OUT/"open-holds.csv"):
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled solver evidence and qualified acceptance","warning":WARNING})
        ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"open-holds.csv",ch); write_csv(CFG/"acceptance-matrix.csv",ca)
    gates=rows(CFG/"gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005","EG-006"}:
            gate["evidence_added"]+=f"; {IDENT} exact local convergence and singularity protocol"
            gate["remaining_evidence"]+="; execute/accept P2 local refinement; H03/H04/dynamics/physical/qualified closure"
    write_csv(CFG/"gate-impact.csv",gates)
    cfg_status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R279","current_records":len(current),"open_holds":len(ch),"acceptance_rows":len(ca),"j2_refinement_protocol":IDENT,"j2_refinement_protocol_executed":False,"r278_h02_closed":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG/"package-status.json").write_text(json.dumps(cfg_status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR279 indexes the unexecuted exact local convergence protocol. R278-H02 and every work authority remain open.\n",encoding="utf-8")
    write_csv(CFG/"source-hash-register.csv",[{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(OUT/"index.html",CFG/"index.html"); manifest(CFG); shutil.copytree(CFG,CFG_REL); manifest(CFG_REL)

    (ROOT/"docs/hr-v0-j2-stop-refinement-protocol-p0.1.md").write_text(f"# HR-V0 J2 stop refinement protocol P0.1\n\n> **{WARNING}**\n\nR279 audits R278 and issues `{IDENT}`. {status['r278_metrics_over_5_percent']} of {status['r278_metrics_audited']} audited 3-to-2 mm metrics change by more than 5%; the uniform P1 study does not close R278-H02. The successor contract uses exact B-Rep physical zones, four local mesh levels, P2 evidence, fixed gauge sections, volume-weighted metrics, GCI and explicit singularity trends.\n\nEven a future protocol pass can establish only numerical convergence of the idealized model. H03 nonlinear contact, H04 joined hardware/frame, dynamics, physical correlation and qualified acceptance remain open.\n\n[Interactive protocol](../release/hr-v0/j2-stop-refinement-protocol-p0.1/index.html)\n",encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md"; old=handoff.read_text(encoding="utf-8")
    handoff.write_text(f"R279 J2 convergence protocol: **`{IDENT}` audits R278 rather than promoting its coarse result. {status['r278_metrics_over_5_percent']}/{status['r278_metrics_audited']} last-pair metrics exceed 5%; exact B-Rep zones, four local mesh levels, P2/GCI/section/singularity evidence are required. R278-H02 stays open and no work authority exists.**\n\n"+old,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; text=ledger.read_text(encoding="utf-8").replace("Two hundred seventy-eight rounds are complete (R01-R278).","Two hundred seventy-nine rounds are complete (R01-R279).")
    text=text.rstrip()+f"\n| R279 | 2026-08-12 | Exact local mesh-convergence and singularity protocol | Codex project-owned analysis-control correction informed by independent factor audit; not an executed analysis or qualified review | R278's 4/3/2 mm uniform P1 study does not resolve the 0.520 mm pocket and several outputs change 6-19%; fixed-hole peaks are idealization-sensitive. | Issued exact B-Rep zones, four locally refined levels, P2/GCI/section-resultant requirements and explicit singularity reporting. R278-H02 remains open; H03/H04 and all physical/qualified gates remain open. | `docs/hr-v0-j2-stop-refinement-protocol-p0.1.md`; `release/hr-v0/j2-stop-refinement-protocol-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.43/` |\n"
    ledger.write_text(text,encoding="utf-8")
    readme=ROOT/"README.md"; text=readme.read_text(encoding="utf-8"); marker="## Start here\n\n"; links="- [R279 exact local J2 convergence protocol](docs/hr-v0-j2-stop-refinement-protocol-p0.1.md)\n- [Interactive R279 convergence guide](release/hr-v0/j2-stop-refinement-protocol-p0.1/index.html)\n- [Interactive configuration reconciliation P0.43](release/hr-v0/configuration-reconciliation-p0.43/index.html)\n"
    text=text.replace(marker,marker+links).replace("Two hundred seventy-eight rounds are complete: R01-R278.","Two hundred seventy-nine rounds are complete: R01-R279.")
    readme.write_text(text,encoding="utf-8")
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print(f"Generated R279 {IDENT} and {CFG_IDENT}; R278-H02 remains open and no work authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
