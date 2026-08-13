#!/usr/bin/env python3
"""Publish R283 J2 execution-architecture evidence and configuration P0.47.

This package deliberately distinguishes a usable exact-geometry execution
architecture from the rejected C07 curved-mesh repair.  It grants no capacity
or physical-work authority.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-execution-architecture-p0.1"
REL = ROOT / "release/hr-v0/j2-execution-architecture-p0.1"
EXACT = ROOT / "mechanical/analysis/hr-v0-j2-exact-zone-submodel-architecture-p0.1"
CURVED = ROOT / "mechanical/analysis/hr-v0-j2-c07-curved-mesh-repair-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.46"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.47"
CFGREL = ROOT / "release/hr-v0/configuration-reconciliation-p0.47"
IDENT = "HR-V0-J2-EXECUTION-ARCHITECTURE-P0.1"
CFGIDENT = "HR-V0-CONFIG-REC-P0.47"
WARNING = (
    "PRELIMINARY - NUMERICAL METHOD ARCHITECTURE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
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
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, object]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{field.replace('_', ' ')}</th>" for field in fields)
    body = "".join(
        "<tr>" + "".join(f"<td>{record.get(field, '')}</td>" for field in fields) + "</tr>"
        for record in records
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    exact_status = json.loads((EXACT / "analysis-status.json").read_text(encoding="utf-8"))
    curved_status = json.loads((CURVED / "analysis-status.json").read_text(encoding="utf-8"))
    if exact_status["r278_h02_closed"] or curved_status["r278_h02_closed"]:
        raise RuntimeError("upstream authority boundary violated")
    if curved_status["bounded_mesh_method_route_found"]:
        raise RuntimeError("R283 package is defined around a rejected curved route")

    for directory in (OUT, REL, CFG, CFGREL):
        if directory.exists():
            shutil.rmtree(directory)
    OUT.mkdir(parents=True)

    findings: list[dict[str, object]] = [
        {"finding_id": "R283-F01", "subject": "exact C07 perimeter identity", "result": "PASS PROTOTYPE", "evidence": "exactly eight ordered curves: four LINE and four R2 CIRCLE; closed endpoint adjacency", "credit": "GEOMETRY IDENTITY METHOD ONLY", "warning": WARNING},
        {"finding_id": "R283-F02", "subject": "C06 root identities", "result": "PARTIAL", "evidence": "one profile curve and four separate thickness-step curves bound; deterministic INBOARD/OUTBOARD and FRONT/BACK convention remains open", "credit": "IDENTITY PREPARATION ONLY", "warning": WARNING},
        {"finding_id": "R283-F03", "subject": "gauges and probes", "result": "PASS PROTOTYPE", "evidence": "exact solid-plane section topology and five +Y pocket-floor face bindings retained", "credit": "DEFINITION METHOD ONLY", "warning": WARNING},
        {"finding_id": "R283-F04", "subject": "raw-run contract", "result": "PASS SCHEMA", "evidence": "nonempty manifest-bound artifact contract includes environment, donor transfer, conservation and Saint-Venant controls", "credit": "EXECUTION ARCHITECTURE ONLY", "warning": WARNING},
        {"finding_id": "R283-F05", "subject": "V04 curved mesh quality", "result": "REJECT", "evidence": "SICN and Q4/Q6/Q8 determinant screens pass, but 897/8999 corner points exceed 1e-9 mm; maximum 0.0863831 mm", "credit": "FAILURE EVIDENCE; NO ROUTE PROMOTED", "warning": WARNING},
        {"finding_id": "R283-F06", "subject": "production numerical execution", "result": "NOT EXECUTED", "evidence": "no clipped cells/facets, structural field, section resultant, submodel transfer or multilevel convergence", "credit": "NONE; H02 OPEN", "warning": WARNING},
    ]
    write_csv(OUT / "finding-register.csv", findings)

    holds_text = [
        "Freeze deterministic C06 profile INBOARD/OUTBOARD parameter direction and FRONT/BACK sign convention",
        "Implement exact cell/zone and facet/zone B-Rep clipping with measure conservation and metric-specific h",
        "Repair C07 curved geometry without unaccepted corner displacement; retain exact facet and B-Rep deviation evidence",
        "Execute curved structural fields, direct clipped quadrature statistics, probes and six-component gauge resultants",
        "Execute donor-transfer conservation and Saint-Venant boundary-distance sensitivity for accepted submodels",
        "Execute L0-L3/L4 or HPC convergence with GCI, singularity trends and complete raw manifests",
        "Obtain independent numerical-method and qualified numerical acceptance before changing H02",
        "Keep nonlinear contact, joined hardware, dynamics, physical correlation, material/DFM/FAI and work authority separate",
    ]
    holds = [{
        "hold_id": f"R283-H{i:02d}", "hold": hold, "state": "OPEN", "execution": "NOT EXECUTED",
        "effect": "R278-H02, capacity, selection, safety credit and all work authority remain blocked", "warning": WARNING,
    } for i, hold in enumerate(holds_text, 1)]
    write_csv(OUT / "open-holds.csv", holds)

    acceptance = [
        {"acceptance_id": "R283-ACC-01", "criterion": "exact C07 eight-edge loop and floor/gauge identities", "execution_state": "BOUNDED PROTOTYPE EXECUTED", "result": "PASS METHOD EVIDENCE; INDEPENDENT ACCEPTANCE OPEN", "evidence_uri": "j2-exact-zone-submodel-architecture-p0.1/", "approver": ""},
        {"acceptance_id": "R283-ACC-02", "criterion": "C06 deterministic subzone semantics", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R283-ACC-03", "criterion": "C07 curved-mesh repair", "execution_state": "V04 EXECUTED", "result": "REJECT - CORNER BIJECTION TOLERANCE FAIL", "evidence_uri": "j2-c07-curved-mesh-repair-p0.1/", "approver": ""},
        {"acceptance_id": "R283-ACC-04", "criterion": "production clipping and direct quadrature structural fields", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R283-ACC-05", "criterion": "submodel transfer and Saint-Venant sensitivity", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R283-ACC-06", "criterion": "accepted multilevel convergence and independent numerical review", "execution_state": "NOT EXECUTED", "result": "OPEN; H02 OPEN", "evidence_uri": "", "approver": ""},
        {"acceptance_id": "R283-ACC-07", "criterion": "separate physical/contact/joint/dynamic/capacity gates", "execution_state": "ENFORCED", "result": "OPEN", "evidence_uri": "", "approver": ""},
    ]
    for record in acceptance:
        record["warning"] = WARNING
    write_csv(OUT / "acceptance-matrix.csv", acceptance)

    inputs = [
        {"source_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "warning": WARNING}
        for path, role in (
            (EXACT / "analysis-status.json", "exact-zone architecture status"),
            (EXACT / "entity-signature-register.csv", "exact topology identities"),
            (EXACT / "raw-run-manifest.schema.json", "raw execution contract"),
            (CURVED / "analysis-status.json", "curved repair status"),
            (CURVED / "variant-register.csv", "V04 bounded screen"),
            (CURVED / "corner-bijection-v04_refined_high_order.csv", "corner correspondence evidence"),
            (ROOT / "tools/publish_hr_v0_j2_execution_architecture_p01.py", "R283 integration publisher"),
        )
    ]
    write_csv(OUT / "exact-input-register.csv", inputs)

    status = {
        "identifier": IDENT, "round": "R283", "date": "2026-08-12",
        "exact_zone_architecture_prototype_pass": True,
        "c07_outer_loop_identity_pass": True,
        "c06_subzone_semantics_complete": False,
        "c07_curved_mesh_route_promoted": False,
        "exact_clipped_zone_execution_complete": False,
        "structural_solution_executed": False,
        "submodel_transfer_executed": False,
        "mesh_convergence_complete": False,
        "independent_numerical_acceptance_complete": False,
        "r278_h02_closed": False,
        "nonlinear_contact_complete": False,
        "joined_joint_complete": False,
        "capacity_established": False,
        "selected": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R283 J2 execution architecture</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--deep:#041a35;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--bad:#8f1d2c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,54px)}}header{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}header>div,main{{max-width:1420px;margin:auto}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.08}}h2{{font-size:clamp(26px,3vw,40px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-size:16px;font-weight:900}}.stop{{background:white;border:3px solid var(--bad);border-radius:14px;padding:20px;margin:28px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white;margin:0 0 28px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--blue);color:white}}@media(max-width:620px){{header,main{{padding:18px 14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R283 · {IDENT}</p><h1>The execution architecture advanced. The curved mesh did not.</h1><p>Exact perimeter, section, probe, provenance and raw-run definitions are now executable method evidence. The refined V04 mesh is rejected because its corner correspondence exceeds the frozen tolerance.</p></div></header><main><section class='stop'><h2>Authority boundary</h2><p>H02 remains open. No structural convergence, capacity, selection, safety credit, fabrication, powered testing, motion or energization authority follows from this package.</p></section><h2>Findings</h2>{table(findings)}<h2>Acceptance state</h2>{table(acceptance)}<h2>Open holds</h2>{table(holds)}</main></body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n> **{WARNING}**\n\nR283 publishes an accepted-for-development exact-zone/submodel execution architecture prototype and rejects the V04 curved-mesh route. H02 and every physical-work gate remain open.\n",
        encoding="utf-8",
    )
    manifest(OUT)
    shutil.copytree(OUT, REL)
    manifest(REL)

    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    new_current = [
        {"record_id": "CFG-66", "role": "R283 exact-zone/submodel execution architecture prototype", "identifier": exact_status["identifier"], "source_path": "release/hr-v0/j2-exact-zone-submodel-architecture-p0.1/analysis-status.json", "configuration_state": "CURRENT METHOD ARCHITECTURE - PRODUCTION CLIPPING/SOLVE OPEN", "release_boundary": "method preparation only; H02 and all authority open", "warning": WARNING},
        {"record_id": "CFG-67", "role": "R283 rejected C07 curved-mesh repair evidence", "identifier": curved_status["identifier"], "source_path": "release/hr-v0/j2-c07-curved-mesh-repair-p0.1/analysis-status.json", "configuration_state": "CURRENT FAILURE EVIDENCE - NO ROUTE PROMOTED", "release_boundary": "no R279-C02/H02/capacity/work credit", "warning": WARNING},
        {"record_id": "CFG-68", "role": "R283 J2 execution-architecture disposition", "identifier": IDENT, "source_path": "release/hr-v0/j2-execution-architecture-p0.1/analysis-status.json", "configuration_state": "CURRENT R283 DISPOSITION - H02 OPEN", "release_boundary": "accepted numerical execution plus independent/qualified review required", "warning": WARNING},
    ]
    current.extend(new_current)
    write_csv(CFG / "current-configuration-map.csv", current)
    cfg_holds = rows(CFG / "open-holds.csv")
    for hold in holds:
        cfg_holds.append({"hold_id": f"HOLD-{len(cfg_holds)+1:03d}", "hold": f"{IDENT}: {hold['hold']}", "state": "OPEN", "closure_evidence": "controlled numerical/physical evidence and independent/qualified acceptance", "warning": WARNING})
    write_csv(CFG / "open-holds.csv", cfg_holds)
    cfg_acceptance = rows(CFG / "acceptance-matrix.csv")
    for record in acceptance:
        cfg_acceptance.append({
            "acceptance_id": f"ACC-{len(cfg_acceptance)+1:03d}",
            "criterion": f"{IDENT}: {record['criterion']}",
            "execution_state": record["execution_state"], "result": record["result"],
            "evidence_uri": record["evidence_uri"], "approver": "", "warning": WARNING,
        })
    write_csv(CFG / "acceptance-matrix.csv", cfg_acceptance)
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({
        "identifier": CFGIDENT, "round": "R283", "current_records": len(current),
        "open_holds": len(cfg_holds), "acceptance_rows": len(cfg_acceptance),
        "j2_execution_architecture": IDENT,
        "j2_exact_zone_architecture_prototype_pass": True,
        "j2_c07_curved_mesh_route_promoted": False,
        "r278_h02_closed": False, "fabrication_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False,
    })
    (CFG / "package-status.json").write_text(json.dumps(cfg_status, indent=2) + "\n", encoding="utf-8")
    write_csv(CFG / "source-hash-register.csv", [{
        "source_path": record["source_path"], "sha256": sha(ROOT / record["source_path"]),
        "role": record["role"], "warning": WARNING,
    } for record in current])
    (CFG / "README.md").write_text(f"# {CFGIDENT}\n\n> **{WARNING}**\n\nR283 indexes the exact-zone execution architecture and rejected C07 curved-mesh repair. H02 and every work authority remain open.\n", encoding="utf-8")
    shutil.copy2(OUT / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFGREL)
    manifest(CFGREL)

    (ROOT / "docs/hr-v0-j2-execution-architecture-p0.1.md").write_text(
        f"# HR-V0 J2 execution architecture P0.1\n\n> **{WARNING}**\n\nR283 freezes the exact C07 eight-edge perimeter, C06 root identities, gauge/probe definitions and raw-run evidence contract. The refined V04 curved mesh passes bounded SICN and determinant screens but is rejected because 897 of 8,999 corner correspondences exceed 1e-9 mm, with 0.0863831 mm maximum displacement. Production clipping, structural fields, submodel transfer, convergence, H02 and every physical gate remain open.\n\n[Interactive R283 guide](../release/hr-v0/j2-execution-architecture-p0.1/index.html)\n",
        encoding="utf-8",
    )
    (ROOT / "docs/reviews/2026-08-12-r283-independent-review-request.md").write_text(
        f"# R283 independent review request\n\n> **{WARNING}**\n\nPlease audit the eight-edge C07 topology identity and adjacency, C06 semantic hold, floor-face probe binding, gauge topology, direct-quadrature arithmetic boundary, raw-run schema, V04 corner-bijection rejection, exact input/runtime provenance, and explicit non-closure of R279-C02, H02, capacity and all work authority.\n",
        encoding="utf-8",
    )
    handoff = ROOT / "docs/handoff-current.md"
    text = handoff.read_text(encoding="utf-8")
    prefix = f"R283 J2 execution architecture: **`{IDENT}` freezes exact geometry/run definitions but rejects the V04 curved mesh. H02, capacity and all physical work remain blocked.**\n\n"
    if not text.startswith(prefix):
        handoff.write_text(prefix + text, encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("Two hundred eighty-two rounds are complete (R01-R282).", "Two hundred eighty-three rounds are complete (R01-R283).")
    if "| R283 |" not in text:
        text = text.rstrip() + f"\n| R283 | 2026-08-12 | Exact-zone/submodel architecture and bounded C07 curved-mesh repair | Codex project-owned execution preparation; independent review requested | R282 froze protocol details but C07 curved geometry and exact-zone execution were not usable. | Exact C07 eight-edge identity, sections, probes and raw-run contract established; V04 rejected for corner correspondence. H02 and all authority remain open. | `docs/hr-v0-j2-execution-architecture-p0.1.md`; `release/hr-v0/j2-execution-architecture-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.47/` |\n"
    ledger.write_text(text, encoding="utf-8")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    links = "- [R283 J2 execution architecture](docs/hr-v0-j2-execution-architecture-p0.1.md)\n- [R283 independent review request](docs/reviews/2026-08-12-r283-independent-review-request.md)\n- [Interactive R283 execution guide](release/hr-v0/j2-execution-architecture-p0.1/index.html)\n- [Interactive configuration reconciliation P0.47](release/hr-v0/configuration-reconciliation-p0.47/index.html)\n"
    if links not in text:
        text = text.replace("## Start here\n\n", "## Start here\n\n" + links)
    text = text.replace("Two hundred eighty-two rounds are complete: R01-R282.", "Two hundred eighty-three rounds are complete: R01-R283.")
    readme.write_text(text, encoding="utf-8")
    config_doc = ROOT / "docs/configuration-management.md"
    text = config_doc.read_text(encoding="utf-8").rstrip()
    line = f"R283 adds `{IDENT}` and `{CFGIDENT}` as fail-closed numerical execution architecture. The exact-zone method advances; the V04 curved mesh is rejected; H02 and all work authority remain open."
    if line not in text:
        config_doc.write_text(text + "\n\n" + line + "\n", encoding="utf-8")
    import generate_hr_v0_collapse_envelope as collapse
    collapse.write_generated_source_manifest()
    print(f"Published R283 {IDENT}; exact architecture advanced, curved route rejected, H02 open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
