#!/usr/bin/env python3
"""Publish R271 C06 FEA evidence and configuration reconciliation P0.35."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mechanical/analysis/hr-v0-j2-stop-fea-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-fea-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.34"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.35"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.35"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
ID = "HR-V0-J2-STOP-FEA-P0.1"
CID = "HR-V0-CONFIG-REC-P0.35"
CAD_ID = "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def manifest(directory: Path) -> None:
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(directory / "file-manifest.csv", rows)


def table(title: str, filename: str, rows: list[dict[str, str]]) -> str:
    fields = list(rows[0])
    head = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row.get(field, ''))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><p><a href='{filename}'>Download {filename}</a></p><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def page() -> str:
    convergence = read_csv(SRC / "mesh-convergence.csv")
    cases = read_csv(SRC / "finest-mesh-load-cases.csv")
    assumptions = read_csv(SRC / "model-assumptions-and-closure.csv")
    holds = read_csv(SRC / "open-holds.csv")
    finest = convergence[-1]
    single = next(row for row in cases if row["case_id"] == "STATIC-PUBLISHED-ENDPOINT-SINGLE")
    twin = next(row for row in cases if row["case_id"] == "STATIC-PUBLISHED-ENDPOINT-EQUAL-TWIN")
    sections = "".join((
        table("Mesh convergence", "mesh-convergence.csv", convergence),
        table("Finest-mesh load cases", "finest-mesh-load-cases.csv", cases),
        table("Model assumptions and closure", "model-assumptions-and-closure.csv", assumptions),
        table("Open holds", "open-holds.csv", holds),
    ))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--bad:#8f1d2c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#0876bd);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}.callout{{background:#ffe8e8;border:3px solid var(--bad);padding:18px;border-radius:14px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metrics div,.figure{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metrics strong{{display:block;font-size:32px;color:var(--blue)}}.figures{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:18px}}.figure img{{display:block;width:100%;height:auto}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:34px 0}}.scroll{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R271 · linear-elastic full-part screen · zero work authority</p><h1>P0.10 fails the strengthened stop screen</h1><p>The exact C06 STEP was tetrahedrally meshed at three sizes and solved with explicit load and restraint assumptions. This is useful rejection evidence—not a nonlinear contact validation.</p></div></header><main><section class='callout'><h2>The beam result was non-conservative</h2><p>The R270 beam screen predicted 50.864 MPa. The 2 mm full-part model produces <strong>{float(single['positive_root_maximum_element_von_mises_mpa_mesh_sensitive']):.3f} MPa</strong> at the positive root and <strong>{float(single['global_maximum_element_von_mises_mpa_mesh_sensitive']):.3f} MPa</strong> globally. Linear 4× scaling gives {float(finest['four_x_linear_scaled_root_max_mpa_not_impact_model']):.3f} MPa and fails the interim geometry-rejection threshold. P0.10 remains unselected.</p></section><section><h2>Finest-mesh evidence</h2><div class='metrics'><div><strong>{int(single['nodes']):,}</strong>nodes</div><div><strong>{int(single['tetrahedra']):,}</strong>tetrahedra</div><div><strong>{float(single['maximum_displacement_mm']):.3f} mm</strong>maximum displacement</div><div><strong>{float(single['positive_root_maximum_element_von_mises_mpa_mesh_sensitive']):.3f} MPa</strong>single-rail root max</div><div><strong>{float(twin['positive_root_maximum_element_von_mises_mpa_mesh_sensitive']):.3f} MPa</strong>equal-twin root max</div><div><strong>9</strong>open holds</div></div></section><section class='figures'><div class='figure'><h2>Mesh sensitivity</h2><img src='mesh-convergence.svg' alt='C06 mesh sensitivity chart'></div><div class='figure'><h2>Centroid stress slice</h2><img src='c06-stress-slice.svg' alt='C06 single-rail endpoint centroid stress slice'></div></section><section class='callout'><h2>What this does not prove</h2><p>Hole surfaces are fully fixed and the contact resultant is distributed over a flat rail-top face. Bolt contact, preload, clearance, slip, prying, frame compliance, C07 contact, local edge stress, material allowables, plasticity, impact, fatigue and physical correlation remain open. Mesh-sensitive maxima are not qualified allowables.</p></section>{sections}</main></body></html>"""


def build_release() -> None:
    for filename in ("README.md", "index.html", "file-manifest.csv"):
        path = SRC / filename
        if path.exists(): path.unlink()
    (SRC / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR271 records a reproducible linear-elastic full-part rejection screen of exact P0.10 C06. The model does not select P0.10 or release fabrication, motion or energization.\n", encoding="utf-8")
    (SRC / "index.html").write_text(page(), encoding="utf-8")
    manifest(SRC)
    if REL.exists(): shutil.rmtree(REL)
    shutil.copytree(SRC, REL)
    manifest(REL)


def update_config() -> None:
    for directory in (CFG, CFGR):
        if directory.exists(): shutil.rmtree(directory)
    shutil.copytree(CFG0, CFG)
    current = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-52", "role": "C06 full-part linear-elastic stop rejection screen", "identifier": ID, "source_path": "release/hr-v0/j2-stop-fea-p0.1/analysis-status.json", "configuration_state": "CURRENT REVIEW EVIDENCE - P0.10 FAILS SCREEN AND IS NOT SELECTED", "release_boundary": "C07/contact/bolts/frame/nonlinearity/dynamics/physical/qualified closure open", "warning": WARNING})
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = read_csv(CFG / "supersession-map.csv")
    supers.append({"record_id": "SUP-49", "prior_identifier": "HR-V0-CONFIG-REC-P0.34", "current_or_required_successor": CID, "disposition": "superseded for package indexing; R270 geometry/load evidence retained with P0.10 failed/unselected", "use_authorized": "NO", "warning": WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    holds = read_csv(CFG / "open-holds.csv")
    for source in read_csv(REL / "open-holds.csv"):
        holds.append({"hold_id": f"HOLD-{len(holds)+1:03d}", "hold": f"{ID}: {source['hold']}", "state": "NOT EXECUTED", "closure_evidence": "NOT EXECUTED", "warning": WARNING})
    write_csv(CFG / "open-holds.csv", holds)
    accept = read_csv(CFG / "acceptance-matrix.csv")
    for source in read_csv(REL / "acceptance-matrix.csv"):
        accept.append({"acceptance_id": f"ACC-{len(accept)+1:03d}", "criterion": f"{ID}: {source['criterion']}", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    write_csv(CFG / "acceptance-matrix.csv", accept)
    impacts = read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-005", "EG-006"}:
            row["evidence_added"] += f"; {ID} exact-C06 three-level linear FEA exposes non-conservative beam result and rejects P0.10"
            row["remaining_evidence"] += "; stronger successor; C07/nonlinear contact/bolt-frame/dynamic/physical correlation and qualified acceptance"
    write_csv(CFG / "gate-impact.csv", impacts)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier": CID, "round": "R271", "current_records": len(current), "supersession_records": len(supers), "open_holds": len(holds), "acceptance_rows": len(accept), "j2_stop_fea_review": ID, "p010_fea_disposition": "FAILS INTERIM FULL-PART SCREEN - UNSELECTED"})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR271 indexes {ID}. P0.8 remains the current unaccepted mechanical identity; P0.10 fails the interim full-part screen and is not selected.\n", encoding="utf-8")
    hashes = []
    for row in current:
        path = ROOT / row["source_path"]
        hashes.append({"source_path": row["source_path"], "sha256": sha(path), "role": row["role"], "warning": WARNING})
    write_csv(CFG / "source-hash-register.csv", hashes)
    shutil.copy2(REL / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def update_records() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical", "mechanical", "bill_of_materials", "commissioning", "assembly"}:
            product["configuration_reconciliation"] = CID
        if product.get("domain") in {"mechanical", "bill_of_materials", "assembly"}:
            if ID not in product.get("supporting_identifiers", []): product.setdefault("supporting_identifiers", []).append(ID)
            if CID not in product.get("supporting_identifiers", []): product.setdefault("supporting_identifiers", []).append(CID)
            product["j2_stop_fea_review"] = ID
            product["p010_fea_disposition"] = "FAILS_INTERIM_FULL_PART_SCREEN_UNSELECTED"
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    (ROOT / "docs/hr-v0-j2-stop-fea-p0.1.md").write_text(f"""# HR-V0 J2 stop C06 full-part FEA screen P0.1

> **{WARNING}**

R271 imports exact P0.10 C06 STEP into Gmsh 4.15.2 and solves three first-order tetrahedral meshes with scikit-fem 12.0.2. The 2 mm mesh contains 9,229 nodes and 39,187 tetrahedra. Under the R270 endpoint-plus-gravity single-rail resultant, the modeled positive-root maximum is 122.205 MPa and the global element maximum is 180.573 MPa; maximum displacement is 0.416 mm. Linear 4× scaling gives 488.822 MPa and fails the interim geometry-rejection threshold.

The result supersedes reliance on the 50.864 MPa beam screen but does not provide qualified convergence or an allowable. Fixed hole surfaces and distributed rail-top loading regularize the actual bolt/contact system. P0.10 remains unselected; nine analysis, physical-correlation and authority holds remain open.

[Interactive R271 evidence](../release/hr-v0/j2-stop-fea-p0.1/index.html)
""", encoding="utf-8")
    readme = ROOT / "README.md"; text = readme.read_text(encoding="utf-8"); marker = "## Start here\n\n"
    links = "- [R271 C06 full-part FEA screen](docs/hr-v0-j2-stop-fea-p0.1.md)\n- [Interactive R271 FEA review](release/hr-v0/j2-stop-fea-p0.1/index.html)\n- [Interactive configuration reconciliation P0.35](release/hr-v0/configuration-reconciliation-p0.35/index.html)\n"
    if links.splitlines()[0] not in text: text = text.replace(marker, marker + links)
    text = text.replace("Two hundred seventy rounds are complete: R01-R270.", "Two hundred seventy-one rounds are complete: R01-R271.")
    readme.write_text(text, encoding="utf-8")
    handoff = ROOT / "docs/handoff-current.md"; prior = handoff.read_text(encoding="utf-8")
    block = f"R271 C06 full-part FEA rejection screen: **`{ID}` imports exact P0.10 C06 into Gmsh/scikit-fem at 4, 3 and 2 mm. The finest single-rail endpoint result is 122.205 MPa at the positive root, 180.573 MPa globally and 0.416 mm displacement; 4× linear scaling is 488.822 MPa and fails the interim geometry screen. Fixed holes and distributed rail loading are screening assumptions, not validated contact/bolt physics. P0.10 remains unselected, all 18 Sol blockers lack qualified closure and energization is prohibited.**\n\n"
    if not prior.startswith("R271 C06 full-part FEA rejection screen:"): handoff.write_text(block + prior, encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"; ledger_text = ledger.read_text(encoding="utf-8")
    ledger_text = ledger_text.replace("Two hundred seventy rounds are complete (R01-R270).", "Two hundred seventy-one rounds are complete (R01-R271).")
    row = "| R271 | 2026-08-12 | Exact-C06 full-part linear FEA rejection screen | Codex project-owned correction responding to R270 analysis holds; not independent or qualified review | R270’s 50.864 MPa beam result omitted the complete plate/boss/hole load path. | Issued three-level Gmsh/scikit-fem evidence. The 2 mm model gives 122.205 MPa root max and rejects P0.10 at the 4× interim screen. Contact, C07, bolt/frame, nonlinear/dynamic, physical and qualified closure remain open; P0.10 is unselected. | `docs/hr-v0-j2-stop-fea-p0.1.md`; `mechanical/analysis/hr-v0-j2-stop-fea-p0.1/`; `release/hr-v0/j2-stop-fea-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.35/` |\n"
    if "| R271 |" not in ledger_text: ledger_text = ledger_text.rstrip() + "\n" + row
    ledger.write_text(ledger_text, encoding="utf-8")


def main() -> int:
    build_release(); update_config(); update_records()
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print("Generated R271 FEA review and P0.35; no authority released")
    return 0


if __name__ == "__main__": raise SystemExit(main())
