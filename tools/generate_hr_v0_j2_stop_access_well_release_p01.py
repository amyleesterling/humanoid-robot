#!/usr/bin/env python3
"""Publish the R273 P0.12 access-well CAD/FEA review and P0.37 index."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-access-well-fea-p0.1"
CAD_REL = ROOT / "release/hr-v0/arm-architecture-p0.12-access-well-stop"
FEA_REL = ROOT / "release/hr-v0/j2-stop-access-well-fea-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.36"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.37"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.37"
CAD_ID = "HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE"
FEA_ID = "HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1"
CFG_ID = "HR-V0-CONFIG-REC-P0.37"
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
        writer.writeheader()
        writer.writerows(records)


def manifest(directory: Path) -> None:
    records = [
        {"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
        for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "file-manifest.csv"
    ]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, str]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row.get(field, ''))}</td>" for field in fields) + "</tr>" for row in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def page() -> str:
    status = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    clearance = json.loads((CAD / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    env = rows(CAD / "a04-fastener-envelope-screen.csv")[0]
    demand = rows(CAD / "a04-joint-demand-screen.csv")[0]
    c06, c07 = status["parts"]["C06"], status["parts"]["C07"]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R273 J2 access-well review</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--hold:#fff1bb;--good:#dff6ea}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#0876bd);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:850;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}h3{{font-size:21px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metrics div,.card{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metrics strong{{display:block;font-size:30px;color:var(--blue)}}.hold{{background:var(--hold);border:3px solid var(--gold);padding:18px;border-radius:12px}}.truth{{background:var(--good);border-left:7px solid #188454;padding:18px}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:32px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R273 &middot; exact P0.12 CAD/linear screen &middot; zero work authority</p><h1>The reinforced stop now has an assemblable access concept.</h1><p>Four rear wells return each C07 screw head to the original 9.525 mm seat. The axes and stop planes stay fixed; actual hardware and the real joined load path remain unselected.</p></div></header><main><section class='metrics'><div><strong>{c07['finest_global_maximum_mpa']:.3f} MPa</strong>C07 linear maximum</div><div><strong>{c07['four_x_global_maximum_mpa']:.3f} MPa</strong>C07 internal 4&times; screen</div><div><strong>{env['radial_head_clearance_mm']} mm</strong>nominal head radial clearance</div><div><strong>{env['screen_thread_beyond_nut_pitches']} pitches</strong>nominal thread beyond screen nut</div><div><strong>{demand['maximum_combined_reaction_n']} N</strong>maximum elastic group demand</div><div><strong>{clearance['minimum_guaranteed_clearance_mm']:.6f} mm</strong>nominal arm clearance floor</div></section><section class='truth'><h2>What changed—and what did not</h2><p>P0.12 removes P0.11's full-thickness bolt grip. The nominal envelope clears the exact XM540 model by more than 18 mm. However, the referenced Accu hardware pages currently report unavailable/offline status, so no purchase order code is released. Supplier quote, received dimensions, torque/locking procedure, preload/slip/prying analysis and proof are still required.</p></section><section class='hold'><h2>Why this still is not a fabrication release</h2><p>The C07 result uses fixed cylindrical surfaces in the original mounting land. It does not model the real screw, washer, nut, S102 compliance, preload, friction, separation, prying, nonlinear stop contact, impact, fatigue or manufacturing tolerances. The 4&times; number is only an internal rejection screen.</p></section><section class='card'><h2>Review the exact artifacts</h2><p><a href='../arm-architecture-p0.12-access-well-stop/HR-V0_arm_architecture_candidate.glb'>3D GLB</a> &middot; <a href='../arm-architecture-p0.12-access-well-stop/HR-V0_arm_architecture_candidate.step'>assembly STEP</a> &middot; <a href='../arm-architecture-p0.12-access-well-stop/a04-fastener-envelope-screen.csv'>fastener envelope</a> &middot; <a href='../arm-architecture-p0.12-access-well-stop/a04-joint-demand-screen.csv'>joint demand</a> &middot; <a href='mesh-convergence.csv'>FEA table</a> &middot; <a href='open-holds.csv'>open holds</a></p></section><section><h2>A04 source and availability record</h2>{table(rows(CAD / 'a04-hardware-source-register.csv'))}</section><section><h2>Mesh sensitivity and results</h2>{table(rows(FEA / 'mesh-convergence.csv'))}</section><section><h2>Acceptance evidence still required</h2>{table(rows(FEA / 'acceptance-matrix.csv'))}</section></main></body></html>"""


def main() -> int:
    for target, source in ((CAD_REL, CAD), (FEA_REL, FEA)):
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
    (FEA / "README.md").write_text(f"# {FEA_ID}\n\n> **{WARNING}**\n\nR273 screens exact P0.12 C06/C07 with C07 restraint returned to the original A04 land. The result is not a joined-load or release analysis.\n", encoding="utf-8")
    (FEA / "index.html").write_text(page(), encoding="utf-8")
    if FEA_REL.exists():
        shutil.rmtree(FEA_REL)
    shutil.copytree(FEA, FEA_REL)
    manifest(CAD_REL)
    manifest(FEA)
    manifest(FEA_REL)

    for target in (CFG, CFG_REL):
        if target.exists():
            shutil.rmtree(target)
    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.extend([
        {"record_id":"CFG-55","role":"unselected collision-screened P0.12 access-well J2 stop CAD","identifier":CAD_ID,"source_path":"release/hr-v0/arm-architecture-p0.12-access-well-stop/p012-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - P0.12 NOT SELECTED","release_boundary":"available exact A04 hardware, installation, joined-load and every physical/qualified closure open","warning":WARNING},
        {"record_id":"CFG-56","role":"P0.12 exact C06/C07 linear structural rejection screen","identifier":FEA_ID,"source_path":"release/hr-v0/j2-stop-access-well-fea-p0.1/analysis-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - INTERNAL SCREEN PASS / UNSELECTED","release_boundary":"joined fastener/contact/dynamic/material/physical/qualified closure open","warning":WARNING},
    ])
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-51","prior_identifier":"HR-V0-CONFIG-REC-P0.36","current_or_required_successor":CFG_ID,"disposition":"superseded for package indexing; P0.11 remains retained review evidence and P0.12 remains unselected","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    holds = rows(CFG / "open-holds.csv")
    for item in rows(FEA / "open-holds.csv"):
        holds.append({"hold_id":f"HOLD-{len(holds)+1:03d}","hold":f"{FEA_ID}: {item['hold']}","state":"NOT EXECUTED","closure_evidence":"NOT EXECUTED","warning":WARNING})
    write_csv(CFG / "open-holds.csv", holds)
    acceptance = rows(CFG / "acceptance-matrix.csv")
    for item in rows(FEA / "acceptance-matrix.csv"):
        acceptance.append({"acceptance_id":f"ACC-{len(acceptance)+1:03d}","criterion":f"{FEA_ID}: {item['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CFG_ID,"round":"R273","current_records":len(current),"supersession_records":len(supers),"open_holds":len(holds),"acceptance_rows":len(acceptance),"p012_candidate":CAD_ID,"p012_fea_review":FEA_ID,"p012_disposition":"PASSES INTERNAL LINEAR REJECTION SCREEN - UNSELECTED","fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CFG_ID}\n\n> **{WARNING}**\n\nR273 indexes P0.12 CAD and linear FEA. P0.8 remains the current unaccepted mechanical identity; P0.12 is not selected.\n", encoding="utf-8")
    hashes = [{"source_path":row["source_path"],"sha256":sha(ROOT / row["source_path"]),"role":row["role"],"warning":WARNING} for row in current]
    write_csv(CFG / "source-hash-register.csv", hashes)
    shutil.copy2(FEA / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFG_REL)
    manifest(CFG_REL)

    doc = ROOT / "docs/hr-v0-j2-stop-access-well-p0.1.md"
    doc.write_text(f"# HR-V0 J2 stop P0.12 access-well candidate\n\n> **{WARNING}**\n\nR273 issues exact `{CAD_ID}` and `{FEA_ID}`. Four 5.20 mm rear access wells restore the original 9.525 mm A04 clamped grip while preserving all A04 axes, the S102 plane and stop contact planes. The nominal dimensional envelope has 0.350 mm radial screw-head clearance, 4.500 pitches beyond the screened nut envelope and more than 18 mm exact-kernel separation from the XM540 model.\n\nThe 2 mm linear C07 model, restrained only at the original A04 land, gives 25.671 MPa and a 102.684 MPa internal 4x screen. The demand-only elastic bolt-group calculation gives a 407.844 N maximum combined reaction. Neither result establishes fastener or frame capacity.\n\nThe previously referenced Accu catalog items are unavailable/offline or lack accepted current purchasability. Exact available screw, washer, prevailing-torque nut and tool order codes remain `SELECTION REQUIRED`, as do torque, anti-galling, locking, reuse, joined-load, nonlinear, dynamic, fatigue, DFM, FAI, physical proof and qualified acceptance. P0.12 is unselected.\n\n[Interactive review](../release/hr-v0/j2-stop-access-well-fea-p0.1/index.html)\n", encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Start here\n\n"
    links = "- [R273 P0.12 access-well J2 stop candidate](docs/hr-v0-j2-stop-access-well-p0.1.md)\n- [R273 validation record](docs/reviews/2026-08-12-r273-validation-record.md)\n- [R273 independent review request](docs/reviews/2026-08-12-r273-independent-review-request.md)\n- [Interactive R273 structural review](release/hr-v0/j2-stop-access-well-fea-p0.1/index.html)\n- [Interactive configuration reconciliation P0.37](release/hr-v0/configuration-reconciliation-p0.37/index.html)\n"
    if links.splitlines()[0] not in text:
        text = text.replace(marker, marker + links)
    text = text.replace("Two hundred seventy-two rounds are complete: R01-R272.", "Two hundred seventy-three rounds are complete: R01-R273.")
    readme.write_text(text, encoding="utf-8")

    handoff = ROOT / "docs/handoff-current.md"
    prior = handoff.read_text(encoding="utf-8")
    block = f"R273 access-well J2 stop candidate: **`{CAD_ID}` restores the original A04 clamped grip and passes nominal clearance; `{FEA_ID}` gives 25.671 MPa C07 and passes the internal linear 4x screen. Exact available hardware, installation controls and the real joined load path remain open. P0.12 is unselected; fabrication, motion and energization remain prohibited.**\n\n"
    if not prior.startswith("R273 access-well J2 stop candidate:"):
        handoff.write_text(block + prior, encoding="utf-8")

    ledger = ROOT / "docs/review-ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("Two hundred seventy-two rounds are complete (R01-R272).", "Two hundred seventy-three rounds are complete (R01-R273).")
    if "| R273 |" not in text:
        text = text.rstrip() + "\n| R273 | 2026-08-12 | C07 access-well fastener-path correction | Codex project-owned CAD/structural/configuration correction; not independent or qualified review | P0.11 passed a geometry screen but required an impractical full-thickness A04 fastener stack; named hardware records were stale or unavailable. | Issued P0.12 with four rear tool wells terminating at the original screw seat, nominal hardware/XM540 envelope and demand-only bolt-group screens, and C07 linear FEA restrained at the original land. Internal screens pass, but exact available hardware, joined-load, nonlinear/dynamic/material/physical/qualified holds remain open; P0.12 is unselected. | `docs/hr-v0-j2-stop-access-well-p0.1.md`; `release/hr-v0/j2-stop-access-well-fea-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.37/` |\n"
    ledger.write_text(text, encoding="utf-8")

    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print("Generated R273 P0.12 review package and P0.37; no authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
