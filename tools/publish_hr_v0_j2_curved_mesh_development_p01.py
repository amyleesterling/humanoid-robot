#!/usr/bin/env python3
"""Publish the fail-closed R284 C07 curved-mesh development disposition."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXED = ROOT / "mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
CONSTRAINED = ROOT / "mechanical/analysis/hr-v0-j2-c07-constrained-high-order-p0.1"
LOCAL = ROOT / "mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-curved-mesh-development-p0.1"
REL = ROOT / "release/hr-v0/j2-curved-mesh-development-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.47"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.48"
CFGREL = ROOT / "release/hr-v0/configuration-reconciliation-p0.48"
IDENT = "HR-V0-J2-CURVED-MESH-DEVELOPMENT-P0.1"
CFGIDENT = "HR-V0-CONFIG-REC-P0.48"
WARNING = (
    "PRELIMINARY - NUMERICAL MESH-METHOD DEVELOPMENT ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_rows(path: Path, records: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for record in records:
        for field in record:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append({
            "relative_path": path.relative_to(directory).as_posix(),
            "sha256": sha(path),
            "bytes": path.stat().st_size,
            "warning": WARNING,
        })
    write_rows(directory / "file-manifest.csv", records)


def copy_release(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def render_table(records: list[dict[str, object]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(record.get(field, '')))}</td>" for field in fields) + "</tr>"
        for record in records
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    fixed_status = json.loads((FIXED / "analysis-status.json").read_text(encoding="utf-8"))
    constrained_status = json.loads((CONSTRAINED / "analysis-status.json").read_text(encoding="utf-8"))
    local_status = json.loads((LOCAL / "analysis-status.json").read_text(encoding="utf-8"))
    if fixed_status["passing_variants"] != ["R284-V06-FINE"]:
        raise RuntimeError("fixed-corner disposition changed")
    if not constrained_status["bounded_constrained_high_order_method_pass"]:
        raise RuntimeError("constrained route no longer passes its bounded screen")
    if local_status["passing_comparator"] != "R284-V06-FINE":
        raise RuntimeError("localization comparator changed")
    if any(s["r278_h02_closed"] for s in (fixed_status, constrained_status, local_status)):
        raise RuntimeError("upstream H02 authority boundary violated")

    for directory in (OUT, REL, CFG, CFGREL):
        if directory.exists():
            shutil.rmtree(directory)
    OUT.mkdir(parents=True)

    findings: list[dict[str, object]] = [
        {"finding_id": "R284-F01", "subject": "V03 fixed-corner mesh", "result": "REJECT", "evidence": "37 wrong-or-zero sampled curved Jacobians across Q4/Q6/Q8", "credit": "FAILURE EVIDENCE ONLY"},
        {"finding_id": "R284-F02", "subject": "V06 fixed-corner mesh", "result": "PASS BOUNDED SCREEN", "evidence": "zero corner relocation; global linear SICN screens pass; zero wrong-or-zero Q4/Q6/Q8 samples", "credit": "CANDIDATE MESH METHOD ONLY"},
        {"finding_id": "R284-F03", "subject": "V08 fixed-corner mesh", "result": "REJECT", "evidence": "9 wrong-or-zero sampled curved Jacobians; finer global sizing is non-monotonic", "credit": "FAILURE EVIDENCE ONLY"},
        {"finding_id": "R284-F04", "subject": "failure localization", "result": "PASS METHOD EVIDENCE", "evidence": "V03: 11 failed elements; V08: 1; failures cluster at backside boss/bore cylinders and the negative-X rail transition", "credit": "TARGETED REMESH INPUT ONLY"},
        {"finding_id": "R284-F05", "subject": "constrained-high-order V04", "result": "PASS BOUNDED ALTERNATE", "evidence": "corners restored exactly; optimized midsides retained; zero wrong-or-zero sampled Q4/Q6/Q8 determinants", "credit": "ALTERNATE METHOD ONLY"},
        {"finding_id": "R284-F06", "subject": "exact facet and B-Rep fidelity", "result": "NOT EXECUTED", "evidence": "boundary-facet identity, surface deviation, loaded area/resultant/location/moment remain unverified", "credit": "NONE"},
        {"finding_id": "R284-F07", "subject": "R279-C02 and H02", "result": "OPEN", "evidence": "no fixed exact-zone histograms, production structural quadrature, multilevel convergence or independent acceptance", "credit": "NONE"},
        {"finding_id": "R284-F08", "subject": "targeted successor remesh", "result": "NOT EXECUTED", "evidence": "expand refinement to backside bosses/rims and both rail transitions from the V06 size basis", "credit": "NEXT DEVELOPMENT ACTION"},
    ]
    for row in findings:
        row["warning"] = WARNING
    write_rows(OUT / "finding-register.csv", findings)

    hold_text = [
        "Freeze exact OCC groups for all backside boss cylinders, rim curves and both rail transitions",
        "Execute a targeted no-high-order-optimizer remesh from the V06 size basis and retain complete raw evidence",
        "Demonstrate repeatability because Gmsh random-seed control is not exposed in the current tool",
        "Produce global and every monitored-zone fixed-bin SICN and signed-Jacobian quality evidence",
        "Retain exact boundary-facet/OCC identities and independently quantify B-Rep surface deviation",
        "Verify curved loaded area, resultant, centroid and moment against the exact B-Rep",
        "Execute production structural quadrature, exact clipped-zone statistics, probes and section resultants",
        "Execute accepted L0-L3/L4 convergence, GCI and singularity trends with complete raw manifests",
        "Obtain independent method verification and qualified numerical acceptance before changing H02",
        "Keep contact, joined hardware, dynamics, material, physical proof and every work authority separate",
    ]
    holds = [{
        "hold_id": f"R284-H{i:02d}", "hold": text, "state": "OPEN", "execution": "NOT EXECUTED",
        "effect": "R279-C02, R278-H02, capacity, selection, safety credit and work authority remain open",
        "warning": WARNING,
    } for i, text in enumerate(hold_text, 1)]
    write_rows(OUT / "open-holds.csv", holds)

    acceptance = [
        {"acceptance_id": "R284-ACC-01", "criterion": "V03/V06/V08 regenerated under one frozen fixed-corner tool revision", "execution_state": "EXECUTED", "result": "PASS PROVENANCE; V06 SOLE BOUNDED PASS", "evidence_uri": "j2-c07-fixed-corner-screen-p0.1/", "approver": ""},
        {"acceptance_id": "R284-ACC-02", "criterion": "failed-element localization and target-feature identification", "execution_state": "EXECUTED", "result": "PASS METHOD EVIDENCE; REMESH OPEN", "evidence_uri": "j2-c07-failure-localization-p0.1/", "approver": ""},
        {"acceptance_id": "R284-ACC-03", "criterion": "constrained-high-order V04 alternate route", "execution_state": "EXECUTED", "result": "PASS BOUNDED SCREEN; INDEPENDENT ACCEPTANCE OPEN", "evidence_uri": "j2-c07-constrained-high-order-p0.1/", "approver": ""},
        {"acceptance_id": "R284-ACC-04", "criterion": "targeted successor remesh with exact added feature groups", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R284-ACC-05", "criterion": "exact facet/B-Rep fidelity and load preservation", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R284-ACC-06", "criterion": "full R279-C02 zone-quality evidence", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R284-ACC-07", "criterion": "accepted multilevel convergence and independent numerical review", "execution_state": "NOT EXECUTED", "result": "OPEN; H02 OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R284-ACC-08", "criterion": "separate contact/joint/dynamic/material/physical/work gates", "execution_state": "ENFORCED", "result": "OPEN", "evidence_uri": "", "approver": ""},
    ]
    for row in acceptance:
        row["warning"] = WARNING
    write_rows(OUT / "acceptance-matrix.csv", acceptance)

    inputs = []
    for path, role in (
        (FIXED / "analysis-status.json", "fixed-corner status"),
        (FIXED / "variant-summary.csv", "three-variant results"),
        (FIXED / "package-manifest.csv", "fixed-corner recursive manifest"),
        (CONSTRAINED / "analysis-status.json", "constrained route status"),
        (CONSTRAINED / "file-manifest.csv", "constrained route manifest"),
        (LOCAL / "analysis-status.json", "failure-localization status"),
        (LOCAL / "failed-element-localization.csv", "failure locations"),
        (LOCAL / "file-manifest.csv", "localization manifest"),
        (ROOT / "tools/publish_hr_v0_j2_curved_mesh_development_p01.py", "R284 integration publisher"),
    ):
        inputs.append({"source_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "warning": WARNING})
    write_rows(OUT / "exact-input-register.csv", inputs)

    status = {
        "identifier": IDENT, "round": "R284", "date": "2026-08-12",
        "fixed_corner_variants_regenerated": True,
        "fixed_corner_sole_bounded_candidate": "R284-V06-FINE",
        "constrained_high_order_bounded_alternate": True,
        "failure_localization_complete": True,
        "bounded_c07_curved_mesh_method_candidate_found": True,
        "targeted_successor_remesh_executed": False,
        "exact_facet_brep_fidelity_complete": False,
        "r279_c02_complete": False,
        "structural_solution_executed": False,
        "mesh_convergence_complete": False,
        "independent_numerical_acceptance_complete": False,
        "r278_h02_closed": False,
        "capacity_established": False, "selected": False, "safety_credit": False,
        "procurement_authorized": False, "fabrication_authorized": False,
        "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R284 C07 curved-mesh development</title><style>:root{{--sky:#dff3ff;--blue:#0a3f73;--deep:#041c38;--gold:#f6c33b;--paper:#f7fbff;--ink:#11263d;--line:#8db9d8;--bad:#8b1e2d;--good:#0d684d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,56px)}}header{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}header>div,main{{max-width:1440px;margin:auto}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.08}}h2{{font-size:clamp(27px,3vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:17px;font-size:16px;font-weight:900}}.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:28px 0}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:20px}}.card strong{{display:block;font-size:clamp(24px,3vw,38px);color:var(--blue)}}.stop{{border-color:var(--bad)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white;margin-bottom:30px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--blue);color:white;position:sticky;top:0}}@media(max-width:620px){{header,main{{padding:18px 14px}}}}</style></head><body><header><div><p class='warning'>{html.escape(WARNING)}</p><p>R284 · {IDENT}</p><h1>One mesh passes a bounded screen. The design is not converged.</h1><p>V06 is the sole fixed-corner candidate. V03 and the finer V08 fail. A constrained-high-order alternate also passes its bounded screen. Exact geometry fidelity, production structural integration and convergence remain open.</p></div></header><main><section class='summary'><div class='card'><strong>1 of 3</strong>fixed-corner variants passed</div><div class='card'><strong>12</strong>failed elements localized across V03 and V08</div><div class='card stop'><strong>OPEN</strong>R279-C02 and R278-H02</div></section><h2>What the evidence says</h2>{render_table(findings)}<h2>Acceptance state</h2>{render_table(acceptance)}<h2>Open work</h2>{render_table(holds)}</main></body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n> **{WARNING}**\n\nR284 identifies V06 and a constrained-high-order alternate as bounded sampled-Jacobian method candidates. The non-monotonic V03/V06/V08 sequence is not convergence; R279-C02, H02 and every physical-work gate remain open.\n",
        encoding="utf-8",
    )
    manifest(OUT)
    copy_release(OUT, REL)

    for source, target in (
        (FIXED, ROOT / "release/hr-v0/j2-c07-fixed-corner-screen-p0.1"),
        (CONSTRAINED, ROOT / "release/hr-v0/j2-c07-constrained-high-order-p0.1"),
        (LOCAL, ROOT / "release/hr-v0/j2-c07-failure-localization-p0.1"),
    ):
        copy_release(source, target)

    shutil.copytree(CFG0, CFG)
    current = read_rows(CFG / "current-configuration-map.csv")
    additions = [
        {"record_id": "CFG-69", "role": "R284 fixed-corner C07 mesh screens", "identifier": fixed_status["identifier"], "source_path": "release/hr-v0/j2-c07-fixed-corner-screen-p0.1/analysis-status.json", "configuration_state": "CURRENT BOUNDED METHOD EVIDENCE - V06 SOLE PASS", "release_boundary": "non-monotonic sampled screen; no R279-C02/H02/capacity/work credit", "warning": WARNING},
        {"record_id": "CFG-70", "role": "R284 constrained-high-order alternate", "identifier": constrained_status["identifier"], "source_path": "release/hr-v0/j2-c07-constrained-high-order-p0.1/analysis-status.json", "configuration_state": "CURRENT BOUNDED ALTERNATE - FIDELITY OPEN", "release_boundary": "exact facet/B-Rep evidence and all higher gates open", "warning": WARNING},
        {"record_id": "CFG-71", "role": "R284 C07 failed-element localization", "identifier": local_status["identifier"], "source_path": "release/hr-v0/j2-c07-failure-localization-p0.1/analysis-status.json", "configuration_state": "CURRENT REMESH INPUT - REMESH NOT EXECUTED", "release_boundary": "localization only; no structural/convergence authority", "warning": WARNING},
        {"record_id": "CFG-72", "role": "R284 C07 curved-mesh development disposition", "identifier": IDENT, "source_path": "release/hr-v0/j2-curved-mesh-development-p0.1/analysis-status.json", "configuration_state": "CURRENT R284 DISPOSITION - H02 OPEN", "release_boundary": "bounded candidate found; production numerical and qualified acceptance required", "warning": WARNING},
    ]
    current.extend(additions)
    write_rows(CFG / "current-configuration-map.csv", current)
    cfg_holds = read_rows(CFG / "open-holds.csv")
    for hold in holds:
        cfg_holds.append({"hold_id": f"HOLD-{len(cfg_holds)+1:03d}", "hold": f"{IDENT}: {hold['hold']}", "state": "OPEN", "closure_evidence": "controlled raw numerical/physical evidence and independent/qualified acceptance", "warning": WARNING})
    write_rows(CFG / "open-holds.csv", cfg_holds)
    cfg_acceptance = read_rows(CFG / "acceptance-matrix.csv")
    for record in acceptance:
        cfg_acceptance.append({"acceptance_id": f"ACC-{len(cfg_acceptance)+1:03d}", "criterion": f"{IDENT}: {record['criterion']}", "execution_state": record["execution_state"], "result": record["result"], "evidence_uri": record["evidence_uri"], "approver": "", "warning": WARNING})
    write_rows(CFG / "acceptance-matrix.csv", cfg_acceptance)
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({
        "identifier": CFGIDENT, "round": "R284", "current_records": len(current),
        "open_holds": len(cfg_holds), "acceptance_rows": len(cfg_acceptance),
        "j2_curved_mesh_development": IDENT,
        "bounded_c07_curved_mesh_method_candidate_found": True,
        "r279_c02_complete": False, "r278_h02_closed": False,
        "capacity_established": False, "selected": False, "safety_credit": False,
        "fabrication_authorized": False, "powered_testing_authorized": False,
        "motion_authorized": False, "energization_authorized": False,
    })
    (CFG / "package-status.json").write_text(json.dumps(cfg_status, indent=2) + "\n", encoding="utf-8")
    write_rows(CFG / "source-hash-register.csv", [{
        "source_path": row["source_path"], "sha256": sha(ROOT / row["source_path"]),
        "role": row["role"], "warning": WARNING,
    } for row in current])
    (CFG / "README.md").write_text(f"# {CFGIDENT}\n\n> **{WARNING}**\n\nR284 indexes bounded C07 mesh-method candidates and targeted failure localization. The sequence is not converged; R279-C02, H02, capacity and every work authority remain open.\n", encoding="utf-8")
    shutil.copy2(OUT / "index.html", CFG / "index.html")
    manifest(CFG)
    copy_release(CFG, CFGREL)

    (ROOT / "docs/hr-v0-j2-curved-mesh-development-p0.1.md").write_text(
        f"# HR-V0 J2 curved-mesh development P0.1\n\n> **{WARNING}**\n\nR284 regenerated three fixed-corner variants under one tool revision. V06 alone passes the bounded global-SICN and sampled Q4/Q6/Q8 Jacobian screens; V03 and the finer V08 fail, so the sequence is not convergence. Failure localization identifies backside boss/bore features and a rail transition for targeted remeshing. A constrained-high-order V04 also passes its bounded screen but lacks exact facet/B-Rep fidelity evidence. R279-C02, R278-H02, capacity, selection, safety credit and every physical-work authority remain open.\n\n[Interactive R284 guide](../release/hr-v0/j2-curved-mesh-development-p0.1/index.html)\n",
        encoding="utf-8",
    )
    (ROOT / "docs/reviews/2026-08-12-r284-independent-review-request.md").write_text(
        f"# R284 independent review request\n\n> **{WARNING}**\n\nPlease independently verify all raw V03/V06/V08 corner, edge, element, OCC, SICN and Q4/Q6/Q8 records; the constrained-high-order alternate; failed-element localization; package/runtime/source manifests; non-monotonic disposition; exact-facet/B-Rep omissions; and explicit non-closure of R279-C02, R278-H02, capacity and all work authority.\n",
        encoding="utf-8",
    )
    (ROOT / "docs/reviews/2026-08-12-r284-validation-record.md").write_text(
        f"# R284 validation record\n\n> **{WARNING}**\n\nProject-owned checkers reproduce V03 fail (37 sampled determinant failures), V06 bounded pass (zero), V08 fail (9), constrained V04 bounded pass, and localization of 12 failed elements across V03/V08. Independent and qualified acceptance remain open.\n",
        encoding="utf-8",
    )
    handoff = ROOT / "docs/handoff-current.md"
    handoff_text = handoff.read_text(encoding="utf-8")
    prefix = f"R284 C07 curved-mesh development: **`{IDENT}` finds bounded method candidates but no convergence. R279-C02, H02, capacity and all physical work remain blocked.**\n\n"
    if not handoff_text.startswith(prefix):
        handoff.write_text(prefix + handoff_text, encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"
    ledger_text = ledger.read_text(encoding="utf-8").replace("Two hundred eighty-three rounds are complete (R01-R283).", "Two hundred eighty-four rounds are complete (R01-R284).")
    if "| R284 |" not in ledger_text:
        ledger_text = ledger_text.rstrip() + "\n| R284 | 2026-08-12 | C07 bounded curved-mesh method candidates and failure localization | Codex project-owned numerical-method development; independent review requested | R283 rejected the high-order-optimized V04 route and left no usable C07 curved-mesh method. | Regenerated fixed-corner V03/V06/V08: V06 alone passes bounded screens; constrained V04 is an alternate; failures localized for targeted remesh. Non-monotonic sequence is not convergence; R279-C02, H02 and all authority remain open. | `docs/hr-v0-j2-curved-mesh-development-p0.1.md`; `release/hr-v0/j2-curved-mesh-development-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.48/` |\n"
    ledger.write_text(ledger_text, encoding="utf-8")
    readme = ROOT / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    links = "- [R284 J2 curved-mesh development](docs/hr-v0-j2-curved-mesh-development-p0.1.md)\n- [R284 independent review request](docs/reviews/2026-08-12-r284-independent-review-request.md)\n- [R284 validation record](docs/reviews/2026-08-12-r284-validation-record.md)\n- [Interactive R284 curved-mesh guide](release/hr-v0/j2-curved-mesh-development-p0.1/index.html)\n- [Interactive configuration reconciliation P0.48](release/hr-v0/configuration-reconciliation-p0.48/index.html)\n"
    if links not in readme_text:
        readme_text = readme_text.replace("## Start here\n\n", "## Start here\n\n" + links)
    readme_text = readme_text.replace("Two hundred eighty-three rounds are complete: R01-R283.", "Two hundred eighty-four rounds are complete: R01-R284.")
    readme.write_text(readme_text, encoding="utf-8")
    config_doc = ROOT / "docs/configuration-management.md"
    config_text = config_doc.read_text(encoding="utf-8").rstrip()
    config_line = f"R284 adds `{IDENT}` and `{CFGIDENT}` as fail-closed curved-mesh development evidence. Bounded candidates exist, but the sequence is non-monotonic and R279-C02, H02 and all work authority remain open."
    if config_line not in config_text:
        config_doc.write_text(config_text + "\n\n" + config_line + "\n", encoding="utf-8")
    import generate_hr_v0_collapse_envelope as collapse
    collapse.write_generated_source_manifest()
    print(f"Published R284 {IDENT}; bounded candidates only, R279-C02/H02 open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
