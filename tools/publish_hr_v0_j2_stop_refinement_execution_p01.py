#!/usr/bin/env python3
"""Publish the R280 bounded refinement-execution feasibility record."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"mechanical/analysis/hr-v0-j2-stop-refinement-execution-p0.1"
REL=ROOT/"release/hr-v0/j2-stop-refinement-execution-p0.1"
CFG0=ROOT/"configuration/hr-v0-config-reconciliation-p0.43"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.44"
CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.44"
IDENT="HR-V0-J2-STOP-REFINEMENT-EXECUTION-P0.1"
CFG_IDENT="HR-V0-CONFIG-REC-P0.44"
WARNING="PRELIMINARY - SCRATCH NUMERICAL EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream:return list(csv.DictReader(stream))


def write_csv(path: Path,records:list[dict[str,object]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(records)


def sha(path: Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory:Path)->None:
    records=[{"relative_path":p.relative_to(directory).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(directory.rglob("*")) if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(directory/"file-manifest.csv",records)


def table(records:list[dict[str,object]])->str:
    fields=list(records[0]);head="".join(f"<th>{html.escape(k.replace('_',' '))}</th>" for k in fields)
    body="".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(k,'')))}</td>" for k in fields)+"</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main()->int:
    for target in (REL,CFG,CFG_REL):
        if target.exists():shutil.rmtree(target)
    status=json.loads((SRC/"execution-status.json").read_text(encoding="utf-8"))
    meshes=rows(SRC/"mesh-register.csv");cases=rows(SRC/"case-results.csv");zones=rows(SRC/"zone-results.csv");attempts=rows(SRC/"attempt-register.csv")
    if status["mesh_convergence_complete"] or status["r278_h02_closed"] or len(meshes)!=3 or len(cases)!=1 or len(attempts)!=2:
        raise RuntimeError("scratch provenance/authority boundary failed")
    c07=next(r for r in meshes if r["part"]=="C07")
    p1=cases[0]
    holds=[
        "Replace the impractical direct sparse P2 solve with a configuration-bound iterative/preconditioned or validated external solver and record residual/error controls",
        "Repair or partition C07 so every mesh level satisfies the R279 SICN quality gate without changing the exact P0.13 geometry or load surfaces",
        "Execute at least three valid refinement levels plus required P2/curved-geometry evidence, section resultants, GCI and singularity trends",
        "Independently review solver verification, exact entity mapping, numerical results and the limited H02-only interpretation",
        "Retain H03 nonlinear contact, H04 joined hardware/frame, dynamics, physical correlation and qualified capacity as separate open gates",
    ]
    write_csv(SRC/"open-holds.csv",[{"hold_id":f"R280-H{i:02d}","hold":h,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS R278-H02 AND P0.13 SELECTION/FABRICATION/MOTION","warning":WARNING} for i,h in enumerate(holds,1)])
    write_csv(SRC/"acceptance-matrix.csv",[{"acceptance_id":f"R280-ACC-{i:02d}","criterion":h,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,h in enumerate(holds,1)])
    page=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R280 J2 refinement feasibility</title><style>:root{{--navy:#082b55;--deep:#041a35;--sky:#7dd3fc;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8;--red:#9b1c1c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05}}h2{{font-size:clamp(26px,3vw,40px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}}.card,.decision{{background:white;border:2px solid var(--line);border-radius:15px;padding:20px}}.card strong{{display:block;font-size:34px;color:var(--navy)}}.decision{{border-left:10px solid var(--red);margin:22px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R280 &middot; {IDENT}</p><h1>The exact mesh path works. The current solver path does not.</h1><p>This bounded execution preserves the failure evidence and names the backend and mesh-quality corrections required next.</p></div></header><main><section class='grid'><div class='card'><strong>3</strong>exact-entity meshes retained</div><div class='card'><strong>1</strong>bounded P1 diagnostic case</div><div class='card'><strong>2</strong>P2 solves stopped for resources</div><div class='card'><strong>{float(c07['min_sicn']):.4f}</strong>C07 minimum SICN: fails ≥0.10</div></section><section class='decision'><h2>R278-H02 remains open</h2><p>The successful P1 case is one level only and receives no convergence or capacity credit. Direct P2 consumed 5.05–7 GB without a result. C07 fails the planned quality gate. The next run needs a controlled iterative/preconditioned or validated external solver plus repaired C07 meshing.</p></section><section><h2>Exact mesh register</h2>{table(meshes)}</section><section><h2>Interrupted solver attempts</h2>{table(attempts)}</section><section><h2>Bounded diagnostic case</h2>{table(cases)}</section><section><h2>Fixed-zone diagnostics</h2>{table(zones)}</section><section><h2>Open holds</h2>{table(rows(SRC/'open-holds.csv'))}</section></main></body></html>"""
    (SRC/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR280 records exact P0.13 entity-tag/local-mesh feasibility, one bounded P1 diagnostic, a C07 quality rejection and two resource-limited P2 attempts. R278-H02 remains open.\n",encoding="utf-8")
    (SRC/"index.html").write_text(page,encoding="utf-8");manifest(SRC);shutil.copytree(SRC,REL);manifest(REL)

    shutil.copytree(CFG0,CFG)
    current=rows(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-63","role":"P0.13 J2 stop exact local-mesh and solver-feasibility execution record","identifier":IDENT,"source_path":"release/hr-v0/j2-stop-refinement-execution-p0.1/execution-status.json","configuration_state":"CURRENT SCRATCH NUMERICAL EVIDENCE - H02 OPEN / NO CAPACITY CREDIT","release_boundary":"solver backend, C07 quality, multi-level convergence, H03/H04/dynamics/physical/qualified closure open","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",current)
    ch,ca=rows(CFG/"open-holds.csv"),rows(CFG/"acceptance-matrix.csv")
    for hold in rows(SRC/"open-holds.csv"):
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled numerical/physical evidence and qualified acceptance","warning":WARNING})
        ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"open-holds.csv",ch);write_csv(CFG/"acceptance-matrix.csv",ca)
    gates=rows(CFG/"gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005","EG-006"}:
            gate["evidence_added"]+=f"; {IDENT} exact tagging/local-mesh and bounded solver-feasibility evidence"
            gate["remaining_evidence"]+="; iterative/validated solver; C07 quality repair; multi-level P2/GCI; H03/H04/dynamics/physical/qualified closure"
    write_csv(CFG/"gate-impact.csv",gates)
    cfg_status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R280","current_records":len(current),"open_holds":len(ch),"acceptance_rows":len(ca),"j2_refinement_execution":IDENT,"j2_refinement_meshes":3,"j2_refinement_cases":1,"j2_direct_p2_results":0,"r278_h02_closed":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG/"package-status.json").write_text(json.dumps(cfg_status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR280 indexes bounded local-mesh/solver feasibility evidence. R278-H02 and every work authority remain open.\n",encoding="utf-8")
    write_csv(CFG/"source-hash-register.csv",[{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(SRC/"index.html",CFG/"index.html");manifest(CFG);shutil.copytree(CFG,CFG_REL);manifest(CFG_REL)

    (ROOT/"docs/hr-v0-j2-stop-refinement-execution-p0.1.md").write_text(f"# HR-V0 J2 stop refinement execution P0.1\n\n> **{WARNING}**\n\nR280 executes a bounded feasibility pass for the R279 protocol. Exact OCC tags and local fields produced three retained meshes. C07 L0 fails the SICN gate at {float(c07['min_sicn']):.6f}. The only completed structural case is C06 L0 P1 with {p1['solution_dofs']} DOFs and receives no convergence/capacity credit. Two direct P2 attempts were interrupted after 5.05–7 GB without a result.\n\nThe next execution requires a controlled iterative/preconditioned or validated external solver, repaired C07 meshing, at least three accepted levels, GCI, section resultants and singularity trends. H02 remains open.\n\n[Interactive execution guide](../release/hr-v0/j2-stop-refinement-execution-p0.1/index.html)\n",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r280-independent-review-request.md").write_text(f"# R280 independent review request\n\n> **{WARNING}**\n\nPlease review `{IDENT}` for exact OCC entity identity, field construction, mesh quality arithmetic, actual versus prospective solution order/DOFs, force balance, fixed-volume diagnostic metrics, clean interruption/resource evidence, and fail-closed interpretation. Confirm that the P1 case supplies no convergence/capacity credit, C07 fails quality, both P2 attempts produced no structural result, and H02/H03/H04 remain open.\n",encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md";old=handoff.read_text(encoding="utf-8")
    if not old.startswith("R280 J2 refinement execution feasibility:"):
        handoff.write_text(f"R280 J2 refinement execution feasibility: **`{IDENT}` proves exact OCC tagging/local fields but rejects the current execution route: C07 L0 fails mesh quality, two direct P2 solves exceed practical memory without results, and the one P1 case has zero convergence/capacity credit. R278-H02 stays open; solver/mesh repair is required.**\n\n"+old,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md";text=ledger.read_text(encoding="utf-8").replace("Two hundred seventy-nine rounds are complete (R01-R279).","Two hundred eighty rounds are complete (R01-R280).")
    if "| R280 |" not in text:
        text=text.rstrip()+f"\n| R280 | 2026-08-12 | Exact local-mesh and solver-feasibility execution | Codex project-owned bounded execution; not independent or qualified review | R279 required exact local zones/P2 evidence, but feasibility in the current toolchain was unknown. | Exact OCC tagging/local fields worked; C07 L0 failed SICN quality; one P1 diagnostic completed with no capacity credit; two direct P2 attempts were cleanly stopped at 5.05-7 GB without results. H02 remains open pending backend/mesh repair and multi-level execution. | `docs/hr-v0-j2-stop-refinement-execution-p0.1.md`; `release/hr-v0/j2-stop-refinement-execution-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.44/` |\n"
    ledger.write_text(text,encoding="utf-8")
    readme=ROOT/"README.md";text=readme.read_text(encoding="utf-8");marker="## Start here\n\n";links="- [R280 bounded J2 refinement execution](docs/hr-v0-j2-stop-refinement-execution-p0.1.md)\n- [R280 independent review request](docs/reviews/2026-08-12-r280-independent-review-request.md)\n- [Interactive R280 execution guide](release/hr-v0/j2-stop-refinement-execution-p0.1/index.html)\n- [Interactive configuration reconciliation P0.44](release/hr-v0/configuration-reconciliation-p0.44/index.html)\n"
    if links.splitlines()[0] not in text:text=text.replace(marker,marker+links)
    text=text.replace("Two hundred seventy-nine rounds are complete: R01-R279.","Two hundred eighty rounds are complete: R01-R280.");readme.write_text(text,encoding="utf-8")
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print(f"Published R280 {IDENT} and {CFG_IDENT}; H02 and all work authority remain open")
    return 0


if __name__=="__main__":raise SystemExit(main())
