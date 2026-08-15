#!/usr/bin/env python3
"""Publish the R270 corrected J2 contact/load model as review evidence."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop"
SRC = ROOT / "mechanical/analysis/hr-v0-j2-stop-bossed-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-bossed-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.33"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.34"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.34"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
ID = "HR-V0-J2-STOP-BOSSED-P0.1"
CAD_ID = "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE"
LOAD_ID = "HR-V0-J2-STOP-LOAD-MODEL-P0.2"
CID = "HR-V0-CONFIG-REC-P0.34"
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
        writer.writeheader()
        writer.writerows(rows)


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


def build_review() -> None:
    for directory in (SRC, REL):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)

    files = (
        "corrected-static-stop-screen.csv",
        "static-geometry-factor-screen.csv",
        "impact-energy-sensitivity.csv",
        "bumper-test-candidate.csv",
        "design-change-register.csv",
        "open-holds.csv",
        "acceptance-matrix.csv",
    )
    for filename in files:
        shutil.copy2(CAD / filename, SRC / filename)
        shutil.copy2(CAD / filename, REL / filename)
    for filename in ("cad-contact-normal-evidence.json", "p010-status.json"):
        shutil.copy2(CAD / filename, SRC / filename)
        shutil.copy2(CAD / filename, REL / filename)

    bindings = []
    for artifact_id, path, role in (
        ("P010-ASSY-STEP", CAD / "HR-V0_arm_architecture_candidate.step", "complete candidate assembly"),
        ("P010-ASSY-GLB", CAD / "HR-V0_arm_architecture_candidate.glb", "interactive 3D assembly"),
        ("P010-ASSY-SVG", CAD / "HR-V0_arm_architecture_candidate.svg", "assembly review view"),
        ("P010-C06-STEP", CAD / "parts/MV0-C06_J2_positive_moving_striker_adapter.step", "integral-boss striker"),
        ("P010-C07-STEP", CAD / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step", "integral-boss catch"),
        ("P010-CONTACT", CAD / "cad-contact-normal-evidence.json", "exact-kernel contact evidence"),
        ("P010-STATIC", CAD / "corrected-static-stop-screen.csv", "corrected single-rail static screen"),
        ("P010-IMPACT", CAD / "impact-energy-sensitivity.csv", "energy sensitivity; inputs unaccepted"),
    ):
        bindings.append({"artifact_id": artifact_id, "source_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "role": role, "authority": "REVIEW EVIDENCE ONLY - NOT RELEASED", "warning": WARNING})
    write_csv(SRC / "artifact-binding.csv", bindings)
    write_csv(REL / "artifact-binding.csv", bindings)

    sources = [
        {"source_id": "R270-SRC-01", "organization": "ROBOTIS", "document": "DYNAMIXEL XM540-W270/R270 e-Manual", "revision_or_date": "live official manual; accessed 2026-08-12", "url": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", "use": "10.6 N m 12 V momentary stall endpoint and caveat", "boundary": "not continuous torque or an allowable", "warning": WARNING},
        {"source_id": "R270-SRC-02", "organization": "Rogers Corporation", "document": "PORON 4790-92-25024-04P data sheet 17-085", "revision_or_date": "rev 1224-PDF (2024); accessed 2026-08-12", "url": "https://rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/data-sheets/17-085-poron-4790-92-25024-p-extra-soft---slow-rebound---supported.pdf", "use": "0.61 +/-0.08 mm candidate coupon properties", "boundary": "not energy-rated and receives no structural stop credit", "warning": WARNING},
        {"source_id": "R270-SRC-03", "organization": "Rogers Corporation", "document": "PORON product availability brochure 17-082", "revision_or_date": "effective 2026-02-27; accessed 2026-08-12", "url": "https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/product-availability/17-082-poron-polyurethanes-product-availability-brochure.pdf", "use": "product 2300327 identity", "boundary": "quote, CoC and availability remain required", "warning": WARNING},
    ]
    write_csv(SRC / "source-register.csv", sources)
    write_csv(REL / "source-register.csv", sources)

    status = json.loads((CAD / "p010-status.json").read_text(encoding="utf-8"))
    status.update({"review_identifier": ID, "date": "2026-08-12", "r269_load_model_disposition": "SUPERSEDED - full radius was not the J2 normal-force moment arm", "all_18_sol_blockers_qualified_closed": False})
    for directory in (SRC, REL):
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        (directory / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR270 corrects the J2 contact-force moment arm and binds an unselected integral-boss CAD candidate. The 4x result is an interim geometry rejection screen only. Twelve physical and qualified holds remain open.\n", encoding="utf-8")

    contact = json.loads((CAD / "cad-contact-normal-evidence.json").read_text(encoding="utf-8"))
    static = read_csv(CAD / "corrected-static-stop-screen.csv")
    factors = read_csv(CAD / "static-geometry-factor-screen.csv")
    sections = "".join(
        (
            table("Corrected static cases", "corrected-static-stop-screen.csv", static),
            table("Interim static geometry factor screen", "static-geometry-factor-screen.csv", factors),
            table("Impact-energy sensitivity", "impact-energy-sensitivity.csv", read_csv(CAD / "impact-energy-sensitivity.csv")),
            table("Bumper test coupon boundary", "bumper-test-candidate.csv", read_csv(CAD / "bumper-test-candidate.csv")),
            table("Open holds", "open-holds.csv", read_csv(CAD / "open-holds.csv")),
        )
    )
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#0876bd);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}.callout{{background:#fff4c9;border:3px solid var(--gold);padding:18px;border-radius:14px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metrics div,.figure{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metrics strong{{display:block;font-size:32px;color:var(--blue)}}.figure img{{display:block;width:100%;height:auto}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:34px 0}}.scroll{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R270 · corrected mechanical review evidence · zero work authority</p><h1>J2 stop: corrected contact physics</h1><p>The exact CAD kernel now supplies the contact point, face normal and J2-axis moment arm. A thicker one-piece stop candidate is generated, but remains unselected.</p></div></header><main><section class='callout'><h2>R269’s 61.344 MPa result is superseded</h2><p>R269 divided torque by the full contact radius. The correct J2 relation is <strong>T<sub>x</sub> = F<sub>n</sub> |(r × n)<sub>x</sub>|</strong>. At the near-contact CAD sample, the governing arm is {float(contact['selected_conservative_solution']['j2_effective_normal_moment_arm_mm']):.6f} mm. P0.10’s single-rail endpoint-plus-gravity beam screen is {static[-1]['nominal_beam_stress_mpa']} MPa. This is not a qualified allowable.</p></section><section><h2>What changed</h2><div class='metrics'><div><strong>15.875 mm</strong>nominal one-piece stock</div><div><strong>16 / 18 mm</strong>striker / catch rails</div><div><strong>{static[-1]['single_rail_normal_force_n']} N</strong>single-rail normal force</div><div><strong>{factors[-1]['factored_stress_mpa']} MPa</strong>4× geometry screen</div><div><strong>12</strong>open holds</div><div><strong>0</strong>released authorities</div></div></section><section class='figure'><h2>Regenerated candidate assembly</h2><img src='../../../cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/HR-V0_arm_architecture_candidate.svg' alt='HR-V0 P0.10 integral-boss J2 stop candidate assembly'><p><a href='../../../cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/HR-V0_arm_architecture_candidate.glb'>Open interactive 3D GLB</a> · <a href='../../../cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/HR-V0_arm_architecture_candidate.step'>Download STEP</a></p></section>{sections}</main></body></html>"""
    (REL / "index.html").write_text(page, encoding="utf-8")
    (SRC / "index.html").write_text(page, encoding="utf-8")
    manifest(SRC)
    manifest(REL)


def update_config() -> None:
    for directory in (CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    shutil.copytree(CFG0, CFG)
    current = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-51", "role": "corrected J2 stop load model and unselected bossed candidate", "identifier": ID, "source_path": "release/hr-v0/j2-stop-bossed-p0.1/package-status.json", "configuration_state": "CURRENT REVIEW EVIDENCE - P0.10 NOT SELECTED", "release_boundary": "R269 load model superseded; analysis/physical/qualified closure open", "warning": WARNING})
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = read_csv(CFG / "supersession-map.csv")
    supers.append({"record_id": "SUP-48", "prior_identifier": "HR-V0-CONFIG-REC-P0.33", "current_or_required_successor": CID, "disposition": "superseded for package indexing; R269 retained as historical evidence with load result superseded", "use_authorized": "NO", "warning": WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    holds = read_csv(CFG / "open-holds.csv")
    for source in read_csv(REL / "open-holds.csv"):
        holds.append({"hold_id": f"HOLD-{len(holds)+1:03d}", "hold": f"{ID}: {source['hold']}", "state": "NOT EXECUTED", "closure_evidence": "NOT EXECUTED", "warning": WARNING})
    write_csv(CFG / "open-holds.csv", holds)
    accept = read_csv(CFG / "acceptance-matrix.csv")
    for source in read_csv(REL / "acceptance-matrix.csv"):
        accept.append({"acceptance_id": f"ACC-{len(accept)+1:03d}", "criterion": f"{ID}: {source['criterion']}", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    write_csv(CFG / "acceptance-matrix.csv", accept)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier": CID, "round": "R270", "current_records": len(current), "supersession_records": len(supers), "open_holds": len(holds), "acceptance_rows": len(accept), "unaccepted_bossed_stop_candidate": CAD_ID, "j2_stop_load_model_review": LOAD_ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR270 supersedes the R269 force conversion and indexes {ID}. P0.8 remains the current unaccepted mechanical identity; P0.10 is not selected.\n", encoding="utf-8")
    hashes = []
    for row in current:
        path = ROOT / row["source_path"]
        hashes.append({"source_path": row["source_path"], "sha256": sha(path), "role": row["role"], "warning": WARNING})
    write_csv(CFG / "source-hash-register.csv", hashes)
    shutil.copy2(REL / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def update_project_records() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical", "mechanical", "bill_of_materials", "commissioning", "assembly"}:
            product["configuration_reconciliation"] = CID
        if product.get("domain") in {"mechanical", "bill_of_materials", "assembly"}:
            for value in (CAD_ID, LOAD_ID, ID, CID):
                if value not in product.get("supporting_identifiers", []):
                    product.setdefault("supporting_identifiers", []).append(value)
            product["unaccepted_bossed_stop_candidate"] = CAD_ID
            product["j2_stop_load_model_review"] = LOAD_ID
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    doc = ROOT / "docs/hr-v0-j2-stop-bossed-p0.1.md"
    doc.write_text(f"""# HR-V0 J2 stop corrected load model and bossed candidate P0.1

> **{WARNING}**

R270 supersedes R269’s `F=T/full radius` calculation. Exact CAD near-contact evidence gives a +Y face normal and a 19.115315 mm effective arm about the J2 +X axis. With the current CAD gravity estimate and the ROBOTIS 12 V momentary endpoint, the unselected P0.10 16 mm × 15 mm minimum single-rail beam screen is 50.864 MPa nominal; the clearly labeled 4× interim geometry rejection value is 203.456 MPa against the project’s provisional 240 MPa MTR threshold.

That pass is not impact physics and is not a release. Contact/root stress concentration, C07, prying, fasteners, extrusion, deformation, fatigue, accepted inertia/speed, motor work, bumper characterization, DFM, FAI and physical tests remain open. Rogers 2300327 is only a proposed sacrificial test coupon ahead of the metal backup and receives no structural-stop credit.

[Interactive R270 evidence](../release/hr-v0/j2-stop-bossed-p0.1/index.html)
""", encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    link = "- [R270 corrected J2 stop model and bossed candidate](docs/hr-v0-j2-stop-bossed-p0.1.md)\n- [Interactive R270 J2 stop review](release/hr-v0/j2-stop-bossed-p0.1/index.html)\n- [Interactive configuration reconciliation P0.34](release/hr-v0/configuration-reconciliation-p0.34/index.html)\n- [R270 validation record](docs/reviews/2026-08-12-r270-validation-record.md)\n- [R270 independent review request](docs/reviews/2026-08-12-r270-independent-review-request.md)\n"
    if "R270 corrected J2 stop model" not in text:
        marker = "## Start here\n\n"
        text = text.replace(marker, marker + link)
    text = text.replace("Two hundred sixty-nine rounds are complete: R01-R269.", "Two hundred seventy rounds are complete: R01-R270.")
    readme.write_text(text, encoding="utf-8")

    handoff = ROOT / "docs/handoff-current.md"
    previous = handoff.read_text(encoding="utf-8")
    block = f"R270 corrected J2 contact/load model: **`{LOAD_ID}` supersedes R269’s non-conservative full-radius force conversion. Exact CAD evidence gives a 19.115315 mm J2 normal-force arm. The unselected `{CAD_ID}` uses integral rear bosses, 16 mm striker rails and 18 mm catches from 15.875 mm nominal stock; its endpoint-plus-gravity nominal beam screen is 50.864 MPa and its 4× interim geometry-rejection screen is 203.456 MPa. The factor is not an impact model or allowable. Twelve physical/qualified holds remain open, all 18 Sol blockers lack qualified closure, and energization is prohibited.**\n\n"
    if not previous.startswith("R270 corrected J2 contact/load model:"):
        handoff.write_text(block + previous, encoding="utf-8")

    ledger = ROOT / "docs/review-ledger.md"
    ledger_text = ledger.read_text(encoding="utf-8")
    ledger_text = ledger_text.replace("Two hundred sixty-nine rounds are complete (R01-R269).", "Two hundred seventy rounds are complete (R01-R270).")
    row = "| R270 | 2026-08-12 | Corrected J2 contact-force model and integral-boss stop candidate | Codex project-owned correction responding to the post-R269 factor/topology audit; not independent or qualified review | R269 used the full contact radius rather than the J2-axis component of r×n, making 61.344 MPa non-conservative. | Issued exact CAD contact evidence, separate static/energy cases and unselected P0.10. The 4× static geometry rejection screen passes, but full load paths, dynamics, DFM/FAI, physical proof and qualified acceptance remain open; all 18 Sol blockers remain without qualified closure. | `docs/hr-v0-j2-stop-bossed-p0.1.md`; `cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/`; `release/hr-v0/j2-stop-bossed-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.34/` |\n"
    if "| R270 |" not in ledger_text:
        ledger_text = ledger_text.rstrip() + "\n" + row
    ledger.write_text(ledger_text, encoding="utf-8")


def main() -> int:
    build_review()
    update_config()
    update_project_records()
    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print("Generated R270 corrected J2 stop review; no authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
