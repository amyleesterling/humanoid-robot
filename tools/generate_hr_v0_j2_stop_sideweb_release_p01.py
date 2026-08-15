#!/usr/bin/env python3
"""Publish R272 P0.11 CAD/FEA review and configuration P0.36."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.11-side-web-stop"
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-sideweb-fea-p0.1"
CAD_REL = ROOT / "release/hr-v0/arm-architecture-p0.11-side-web-stop"
FEA_REL = ROOT / "release/hr-v0/j2-stop-sideweb-fea-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.35"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.36"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.36"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
CAD_ID = "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE"
FEA_ID = "HR-V0-J2-STOP-SIDEWEB-FEA-P0.1"
CFG_ID = "HR-V0-CONFIG-REC-P0.36"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def manifest(directory: Path) -> None:
    records = [{"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING} for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, str]]) -> str:
    fields = list(records[0])
    return "<div class='scroll'><table><thead><tr>" + "".join(f"<th>{html.escape(field.replace('_',' '))}</th>" for field in fields) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{html.escape(row.get(field,''))}</td>" for field in fields) + "</tr>" for row in records) + "</tbody></table></div>"


def page() -> str:
    status = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    clearance = json.loads((CAD / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    c06, c07 = status["parts"]["C06"], status["parts"]["C07"]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R272 J2 stop review</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--hold:#fff1bb}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#0876bd);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:850;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metrics div,.card{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metrics strong{{display:block;font-size:30px;color:var(--blue)}}.hold{{background:var(--hold);border:3px solid var(--gold);padding:18px;border-radius:12px}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:32px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R272 &middot; exact mixed-side C06/C07 candidate &middot; zero work authority</p><h1>A stronger stop candidate survives the internal screen.</h1><p>P0.11 moves C06 reinforcement away from the actuator, carries C07 through its four-bolt pattern, and retunes the striker datum for nominal 118-degree contact. It remains unselected.</p></div></header><main><section class='metrics'><div><strong>{c06['finest_global_maximum_mpa']:.3f} MPa</strong>C06 global maximum</div><div><strong>{c06['four_x_global_maximum_mpa']:.3f} MPa</strong>C06 4&times; screen</div><div><strong>{c07['finest_global_maximum_mpa']:.3f} MPa</strong>C07 global maximum</div><div><strong>{c07['four_x_global_maximum_mpa']:.3f} MPa</strong>C07 4&times; screen</div><div><strong>{clearance['minimum_guaranteed_clearance_mm']:.6f} mm</strong>nominal clearance floor</div><div><strong>12</strong>open holds</div></section><section class='hold'><h2>Why this is not released</h2><p>C07 now requires a new through-thickness M2.5 stack. Bolt preload, bearing, prying, frame compliance, nonlinear contact, tolerance, dynamics, material allowables, DFM, FAI and physical correlation remain open. The 4&times; value is an internal rejection screen, not an impact model or safety factor.</p></section><section class='card'><h2>Review the exact artifacts</h2><p><a href='../arm-architecture-p0.11-side-web-stop/HR-V0_arm_architecture_candidate.glb'>Interactive 3D GLB</a> &middot; <a href='../arm-architecture-p0.11-side-web-stop/HR-V0_arm_architecture_candidate.step'>Assembly STEP</a> &middot; <a href='mesh-convergence.csv'>FEA table</a> &middot; <a href='open-holds.csv'>Open holds</a></p></section><section><h2>Mesh sensitivity and results</h2>{table(rows(FEA / 'mesh-convergence.csv'))}</section><section><h2>Acceptance evidence still required</h2>{table(rows(FEA / 'acceptance-matrix.csv'))}</section></main></body></html>"""


def main() -> int:
    for target, source in ((CAD_REL, CAD), (FEA_REL, FEA)):
        if target.exists(): shutil.rmtree(target)
        shutil.copytree(source, target)
    (FEA / "README.md").write_text(f"# {FEA_ID}\n\n> **{WARNING}**\n\nR272 screens exact P0.11 C06/C07. Both pass the internal 4x geometry-rejection screen; neither is selected or released.\n", encoding="utf-8")
    (FEA / "index.html").write_text(page(), encoding="utf-8")
    if FEA_REL.exists(): shutil.rmtree(FEA_REL)
    shutil.copytree(FEA, FEA_REL)
    manifest(CAD_REL); manifest(FEA); manifest(FEA_REL)

    for target in (CFG, CFG_REL):
        if target.exists(): shutil.rmtree(target)
    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.extend([
        {"record_id":"CFG-53","role":"unselected collision-screened P0.11 mixed-side J2 stop CAD","identifier":CAD_ID,"source_path":"release/hr-v0/arm-architecture-p0.11-side-web-stop/p011-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - P0.11 NOT SELECTED","release_boundary":"new C07 fastener stack and all physical/qualified closure open","warning":WARNING},
        {"record_id":"CFG-54","role":"P0.11 exact C06/C07 linear structural rejection screen","identifier":FEA_ID,"source_path":"release/hr-v0/j2-stop-sideweb-fea-p0.1/analysis-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - INTERNAL SCREEN PASS / UNSELECTED","release_boundary":"contact/joint/dynamic/material/physical/qualified closure open","warning":WARNING},
    ])
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-50","prior_identifier":"HR-V0-CONFIG-REC-P0.35","current_or_required_successor":CFG_ID,"disposition":"superseded for package indexing; P0.10 rejection retained and P0.11 remains unselected","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    holds = rows(CFG / "open-holds.csv")
    for item in rows(FEA / "open-holds.csv"):
        holds.append({"hold_id":f"HOLD-{len(holds)+1:03d}","hold":f"{FEA_ID}: {item['hold']}","state":"NOT EXECUTED","closure_evidence":"NOT EXECUTED","warning":WARNING})
    write_csv(CFG / "open-holds.csv", holds)
    accept = rows(CFG / "acceptance-matrix.csv")
    for item in rows(FEA / "acceptance-matrix.csv"):
        accept.append({"acceptance_id":f"ACC-{len(accept)+1:03d}","criterion":f"{FEA_ID}: {item['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", accept)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CFG_ID,"round":"R272","current_records":len(current),"supersession_records":len(supers),"open_holds":len(holds),"acceptance_rows":len(accept),"p011_candidate":CAD_ID,"p011_fea_review":FEA_ID,"p011_disposition":"PASSES INTERNAL LINEAR REJECTION SCREEN - UNSELECTED"})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CFG_ID}\n\n> **{WARNING}**\n\nR272 indexes P0.11 CAD and linear FEA. P0.8 remains current unaccepted mechanical identity; P0.11 is not selected.\n", encoding="utf-8")
    hashes = [{"source_path":row["source_path"],"sha256":sha(ROOT / row["source_path"]),"role":row["role"],"warning":WARNING} for row in current]
    write_csv(CFG / "source-hash-register.csv", hashes)
    shutil.copy2(FEA / "index.html", CFG / "index.html")
    manifest(CFG); shutil.copytree(CFG, CFG_REL); manifest(CFG_REL)

    # P0.11 is unselected review evidence. Do not attach it to current release
    # products or advance their P0.35 configuration reconciliation pointer.

    doc = ROOT / "docs/hr-v0-j2-stop-sideweb-p0.1.md"
    doc.write_text(f"# HR-V0 J2 stop P0.11 mixed-side candidate\n\n> **{WARNING}**\n\nR272 issues exact `{CAD_ID}` and `{FEA_ID}`. Nominal 15..120 degree clearance is certified at no less than 0.764678 mm. Under the exact 253.607 N endpoint-plus-gravity resultant, the 2 mm linear models give 17.915 MPa C06 and 7.845 MPa C07 global maxima; their 4x internal screens are 71.659 and 31.380 MPa.\n\nC07 now carries its rear web through the four M2.5 axes, requiring a new unreleased fastener stack. Nonlinear contact, bolt/frame behavior, dynamics, material allowables, DFM, FAI, physical proof and qualified acceptance remain open. P0.11 is unselected.\n\n[Interactive review](../release/hr-v0/j2-stop-sideweb-fea-p0.1/index.html)\n",encoding="utf-8")
    readme = ROOT / "README.md"; text = readme.read_text(encoding="utf-8"); marker="## Start here\n\n"; links="- [R272 P0.11 mixed-side J2 stop candidate](docs/hr-v0-j2-stop-sideweb-p0.1.md)\n- [R272 validation record](docs/reviews/2026-08-12-r272-validation-record.md)\n- [R272 independent review request](docs/reviews/2026-08-12-r272-independent-review-request.md)\n- [Interactive R272 structural review](release/hr-v0/j2-stop-sideweb-fea-p0.1/index.html)\n- [Interactive configuration reconciliation P0.36](release/hr-v0/configuration-reconciliation-p0.36/index.html)\n"
    if links.splitlines()[0] not in text: text=text.replace(marker,marker+links)
    text=text.replace("Two hundred seventy-one rounds are complete: R01-R271.","Two hundred seventy-two rounds are complete: R01-R272.")
    readme.write_text(text,encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md"; prior=handoff.read_text(encoding="utf-8"); block=f"R272 mixed-side J2 stop candidate: **`{CAD_ID}` passes nominal continuous clearance and `{FEA_ID}` passes the internal linear 4x geometry screen. C07 now requires a new through-thickness M2.5 stack. P0.11 remains unselected; nonlinear contact, joined load path, dynamics, physical proof and qualified release remain open; energization is prohibited.**\n\n"
    if not prior.startswith("R272 mixed-side J2 stop candidate:"): handoff.write_text(block+prior,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; text=ledger.read_text(encoding="utf-8").replace("Two hundred seventy-one rounds are complete (R01-R271).","Two hundred seventy-two rounds are complete (R01-R272).")
    if "| R272 |" not in text: text=text.rstrip()+"\n| R272 | 2026-08-12 | Mixed-side through-bolt-web J2 stop correction | Codex project-owned structural/collision correction; not independent or qualified review | P0.10 failed full-part FEA; early P0.11 web variants either collided or failed C07. | Issued collision-screened P0.11 with contact-side C06 reinforcement and rear-side C07 reinforcement through four M2.5 axes. Exact-load linear screens pass internally, but the new fastener stack, contact/joint/dynamic/material/physical/qualified holds remain open; P0.11 is unselected. | `docs/hr-v0-j2-stop-sideweb-p0.1.md`; `release/hr-v0/j2-stop-sideweb-fea-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.36/` |\n"
    ledger.write_text(text,encoding="utf-8")
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print("Generated R272 review package and P0.36; no authority released")
    return 0


if __name__ == "__main__": raise SystemExit(main())
