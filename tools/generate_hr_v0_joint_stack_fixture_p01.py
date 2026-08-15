#!/usr/bin/env python3
"""Generate R252 zero-energy joint-stack metrology fixture candidate."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as arm  # noqa: E402

ID = "HR-V0-JOINT-STACK-FIXTURE-P0.1"
CID = "HR-V0-CONFIG-REC-P0.16"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "test-fixtures" / "hr-v0" / "joint-stack-fixture-p0.1"
REL = ROOT / "release" / "hr-v0" / "joint-stack-fixture-p0.1"
OLD = ROOT / "configuration" / "hr-v0-config-reconciliation-p0.15"
CFG = ROOT / "configuration" / "hr-v0-config-reconciliation-p0.16"
CFGR = ROOT / "release" / "hr-v0" / "configuration-reconciliation-p0.16"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
SOURCE_STEP = {
    "XM540": VENDOR / "XMHD-540.N101.I101.STP",
    "H101": VENDOR / "FR13-H101K.stp",
    "S102": VENDOR / "FR13-S102K.stp",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in rows)


def warning_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(row, warning=WARNING) for row in rows]


def manifest(directory: Path) -> None:
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], rows)


def joint_geometry() -> dict[str, cq.Shape]:
    xm540 = arm.rotate_x(arm.actuator_to_joint_frame(cq.importers.importStep(str(SOURCE_STEP["XM540"])).val()), 90.0)
    h101 = cq.importers.importStep(str(SOURCE_STEP["H101"])).val()
    s102 = arm.rotate_x(cq.importers.importStep(str(SOURCE_STEP["S102"])).val(), 90.0)
    return {"XM540": xm540, "H101": h101, "S102": s102}


def fixture_geometry(parts: dict[str, cq.Shape]) -> tuple[dict[str, cq.Shape], list[dict[str, object]]]:
    # These are review envelopes, not machinable definitions. The fixed S102
    # outer frame face is nominally Y=-51.5 after the controlled Rx90 transform.
    # Six point-contact candidates touch only that face and stay 6.75 mm from
    # the nominal actuator STEP. Their compliant material/force remains held.
    base = cq.Solid.makeBox(160, 120, 12, cq.Vector(-80, -94, -60))
    left = cq.Solid.makeBox(12, 78, 96, cq.Vector(-70, -82, -48))
    right = cq.Solid.makeBox(12, 78, 96, cq.Vector(58, -82, -48))
    bridge = cq.Solid.makeBox(116, 12, 12, cq.Vector(-58, -82, 36))
    contact_points = [(-19, -5), (19, -5), (0, 15), (-18, 0), (18, 0), (0, -15)]
    contacts: list[cq.Shape] = []
    rows: list[dict[str, object]] = []
    for index, (x, z) in enumerate(contact_points, 1):
        radius = 2.0
        contact = cq.Solid.makeSphere(radius, cq.Vector(x, -51.5 - radius, z))
        contacts.append(contact)
        rows.append({
            "contact_id": f"JFX-CP-{index:02d}",
            "article_feature": "FR13-S102K transformed outer frame face at nominal Y=-51.500 mm",
            "nominal_center_xyz_mm": f"{x:.3f},{-53.5:.3f},{z:.3f}",
            "nominal_contact_xyz_mm": f"{x:.3f},-51.500,{z:.3f}",
            "candidate_contact_radius_mm": "2.000 REVIEW ENVELOPE",
            "nominal_s102_distance_mm": f"{contact.distance(parts['S102']):.9f}",
            "nominal_xm540_distance_mm": f"{contact.distance(parts['XM540']):.9f}",
            "material": "SELECTION REQUIRED - compliant non-marring material",
            "maximum_contact_force": "SELECTION REQUIRED",
            "state": "GEOMETRY SCREEN ONLY - RECEIVED FIT AND QUALIFIED ACCEPTANCE REQUIRED",
        })
    fixture = {
        "JFX_BASE_REVIEW_ENVELOPE": base,
        "JFX_LEFT_SUPPORT_REVIEW_ENVELOPE": left,
        "JFX_RIGHT_SUPPORT_REVIEW_ENVELOPE": right,
        "JFX_BRIDGE_REVIEW_ENVELOPE": bridge,
    }
    for index, contact in enumerate(contacts, 1):
        fixture[f"JFX_COMPLIANT_CONTACT_{index:02d}_SELECTION_REQUIRED"] = contact
    return fixture, rows


def guide_page(
    directory: Path,
    names: list[str],
    *,
    identifier: str = ID,
    heading: str = "Zero-energy joint-stack fixture candidate",
    lede: str = "Review geometry and a fail-closed temporary-stack instruction for the R251 first physical shop session.",
    status: str = "FIXTURE NOT BUILDABLE &middot; TEMPORARY ASSEMBLY NOT AUTHORIZED &middot; NO POWER OR MOTION &middot; ALL RESULTS BLANK",
    include_model: bool = True,
) -> str:
    sections = []
    for name in names:
        rows, fields = read_csv(directory / name)
        head = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[field]))}</td>" for field in fields) + "</tr>" for row in rows)
        sections.append(f"<section><h2>{name[:-4].replace('-', ' ').title()}</h2><p><a href='{name}'>Download {name}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>")
    model_script = "<script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js'></script>" if include_model else ""
    model_section = "<section><h2>Inspect the candidate</h2><model-viewer src='HR-V0_joint-stack-fixture_P0.1_review.glb' alt='Preliminary joint-stack fixture and exact ROBOTIS geometry' camera-controls shadow-intensity='0.8'></model-viewer><p>The dark-blue frame is a review envelope only. Gold spheres are held compliant contact candidates; exact material and force remain selection required.</p></section>" if include_model else ""
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{identifier}</title>{model_script}<style>:root{{--ink:#082a4a;--blue:#075ea8;--sky:#dff3ff;--gold:#f3bd28;--paper:#f8fbfd;--line:#9bc6e4;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}.warning{{font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd;border:3px solid var(--gold);padding:14px;border-radius:12px}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05}}h2{{font-size:clamp(24px,2.6vw,36px)}}.status{{font-size:18px;font-weight:800;color:var(--danger)}}model-viewer{{width:100%;height:600px;background:var(--sky);border:2px solid var(--line);border-radius:14px}}a{{font-size:16px;font-weight:700;color:var(--blue)}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:34px}}model-viewer{{height:430px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><h1>{heading}</h1><p>{lede}</p></div></header><main><p class='status'>{status}</p>{model_section}{''.join(sections)}</main></body></html>"""


def build_package() -> None:
    for directory in (OUT, REL):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
    parts = joint_geometry()
    fixture, contact_rows = fixture_geometry(parts)
    model = {"EXACT_XM540_VENDOR_GEOMETRY": parts["XM540"], "EXACT_FR13_H101K_VENDOR_GEOMETRY": parts["H101"], "EXACT_FR13_S102K_VENDOR_GEOMETRY": parts["S102"], **fixture}
    assembly = cq.Assembly(name="HR_V0_JOINT_STACK_FIXTURE_P01_NOT_RELEASED")
    for name, shape in model.items():
        if "CONTACT" in name:
            color = cq.Color(0.95, 0.70, 0.10)
        elif "JFX_" in name:
            color = cq.Color(0.08, 0.28, 0.52)
        elif "XM540" in name:
            color = cq.Color(0.15, 0.55, 0.82)
        else:
            color = cq.Color(0.72, 0.76, 0.79)
        assembly.add(shape, name=name, color=color)
    step_path = OUT / "HR-V0_joint-stack-fixture_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(model.values())), str(step_path))
    arm.canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_joint-stack-fixture_P0.1_review.glb"))

    source_rows = []
    for source_id, label, path, date in (
        ("JFX-SRC-01", "XM540 controlled STEP", SOURCE_STEP["XM540"], "drawing date 2019-03-18; controlled 2026-08-06"),
        ("JFX-SRC-02", "FR13-H101K controlled STEP", SOURCE_STEP["H101"], "drawing date 2026-01-07; controlled 2026-08-06"),
        ("JFX-SRC-03", "FR13-S102K controlled STEP", SOURCE_STEP["S102"], "drawing date 2026-01-07; controlled 2026-08-06"),
        ("JFX-SRC-04", "R251 first-shop-session status", ROOT / "release/hr-v0/first-shop-session-p0.1/package-status.json", "R251 / 2026-08-11"),
        ("JFX-SRC-05", "R84 joint-stack traveler", ROOT / "test-fixtures/hr-v0/joint-stack-metrology-p0.1/operation-sequence.csv", "R84 / 2026-08-08"),
    ):
        source_rows.append({"source_id": source_id, "source": label, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "revision_or_date": date, "use": "BOUND INPUT - DOES NOT AUTHORIZE WORK"})
    write_csv(OUT / "source-binding.csv", ["source_id", "source", "path", "sha256", "revision_or_date", "use", "warning"], warning_rows(source_rows))
    write_csv(OUT / "contact-zone-register.csv", ["contact_id", "article_feature", "nominal_center_xyz_mm", "nominal_contact_xyz_mm", "candidate_contact_radius_mm", "nominal_s102_distance_mm", "nominal_xm540_distance_mm", "material", "maximum_contact_force", "state", "warning"], warning_rows(contact_rows))

    keepouts = [
        ("JFX-KO-01", "XM540 case, covers, output/idler and all actuator surfaces", "NO CONTACT OR LOAD"),
        ("JFX-KO-02", "XM540 connector and connector-side recess", "NO CONTACT; NO CABLE PRESENT"),
        ("JFX-KO-03", "H101 broad/side faces and all attachment holes during articulation", "NO FIXTURE CONTACT"),
        ("JFX-KO-04", "S102 holes, bends, edge radii and side ears", "NO CONTACT"),
        ("JFX-KO-05", "all candidate hard-stop, bumper, guard and service-tool regions", "NO CONTACT OR INFERRED CLEARANCE"),
        ("JFX-KO-06", "joint swept envelope outside the fixed S102 contact face", "REVIEWED FREE SPACE REQUIRED"),
    ]
    write_csv(OUT / "keepout-register.csv", ["keepout_id", "region", "rule", "verification", "state", "warning"], warning_rows([{"keepout_id": i, "region": r, "rule": rule, "verification": "received article/fixture overlay, feeler/visual evidence and signed review", "state": "NOT EXECUTED"} for i, r, rule in keepouts]))

    temp_steps = [
        ("JFX-TMP-001", "Verify zero-energy area and prohibit every power source, U2D2 and actuator cable.", "JSM-HP-006", "No source-capable item present", "STOP/REMOVE/REINSPECT"),
        ("JFX-TMP-002", "Reconcile received actuator, H101, S102, idler, thrust washer, spacer rings and supplied screws to serial/lot inventory.", "JSM-HP-002", "Exact identities and intact parts", "QUARANTINE/NCR"),
        ("JFX-TMP-003", "Complete loose-part dimensions, thread-depth and screw-length measurements before any threaded assembly.", "JSM-HP-003", "Accepted raw measurements and uncertainty", "NO ASSEMBLY"),
        ("JFX-TMP-004", "Qualified reviewer selects exact screw allocation, spacer placement, temporary torque, tool, locking prohibition and reuse/disposition.", "JSM-HP-005", "Signed configuration-bound instruction", "NO SCREW ENTERS ACTUATOR"),
        ("JFX-TMP-005", "Trial-fit the received fixture with no screw installed; prove only approved contacts engage and every keepout remains clear.", "JSM-HP-004", "Signed photographs/overlay/clearance record", "REMOVE FIXTURE/NCR"),
        ("JFX-TMP-006", "Install thrust washer and align manufacturer index marks exactly as accepted from current ROBOTIS instructions.", "JSM-HP-005", "Photographic evidence before cover-up", "DISASSEMBLE/NCR"),
        ("JFX-TMP-007", "Install S102 and H101/idler/spacer stack using only the signed temporary hardware instruction; no cable or threadlocker.", "JSM-HP-005/006", "No gap, bottoming, distortion or unexpected resistance", "STOP/DO NOT FORCE"),
        ("JFX-TMP-008", "Place the fixed S102 frame against the six held contact candidates with zero preload beyond gravity plus the accepted restraint.", "JSM-HP-004", "Article stable; case/connector/H101 remain unloaded", "SUPPORT BY HAND/REMOVE"),
        ("JFX-TMP-009", "Apply the selected secondary restraint solely against tipping/escape; record contact force and prove it cannot become a rotation stop.", "JSM-HP-004", "SELECTION REQUIRED acceptance", "NO ARTICULATION"),
        ("JFX-TMP-010", "Hand-position only within the signed pose list while an independent witness verifies all keepouts continuously.", "JSM-HP-007", "No slip, contact, force or use of actuator/fixture as stop", "STOP/QUARANTINE/NCR"),
        ("JFX-TMP-011", "Execute JSM-OP-011..016, hash all evidence and preserve configuration identity.", "JSM-HP-007/008", "Complete raw records", "HOLD ASSEMBLED"),
        ("JFX-TMP-012", "Unload, teardown with the signed reverse sequence, inspect every article and re-quarantine.", "JSM-HP-008", "No damage/galling/debris/deformation; complete inventory", "QUARANTINE/NCR"),
    ]
    write_csv(OUT / "temporary-stack-instruction.csv", ["step_id", "instruction", "hold_point", "acceptance", "failure_action", "execution_state", "evidence_uri", "signer", "warning"], warning_rows([{"step_id": i, "instruction": a, "hold_point": h, "acceptance": ok, "failure_action": fail, "execution_state": "NOT EXECUTED", "evidence_uri": "", "signer": ""} for i, a, h, ok, fail in temp_steps]))

    selections = [
        ("JFX-SEL-01", "fixture structural material and process", "received geometry, handling load and metrology compatibility"),
        ("JFX-SEL-02", "six compliant contact materials", "hardness, compression set, friction, cleanliness and non-marring evidence"),
        ("JFX-SEL-03", "maximum contact force/preload", "received article allowables and repeatability study"),
        ("JFX-SEL-04", "secondary restraint topology and force", "tip/escape load case without becoming a rotation stop"),
        ("JFX-SEL-05", "fixture manufacturing tolerances and datum scheme", "qualified mechanical/metrology review"),
        ("JFX-SEL-06", "fixture fasteners/torques/locking/reuse", "complete load path and received proof"),
        ("JFX-SEL-07", "article screw identities/lengths", "received kit inventory and thread-depth measurements"),
        ("JFX-SEL-08", "spacer-ring allocation", "received inventory and manufacturer instruction reconciliation"),
        ("JFX-SEL-09", "temporary article torque/tool", "manufacturer/qualified reviewer evidence and calibrated tool"),
        ("JFX-SEL-10", "temporary screw reuse/disposition", "manufacturer or qualified engineering disposition"),
        ("JFX-SEL-11", "approved hand-positioned pose list", "received interference/fixture/keepout review"),
        ("JFX-SEL-12", "fixture calibration/verification method", "accepted uncertainty budget and repeatability evidence"),
    ]
    write_csv(OUT / "selection-register.csv", ["selection_id", "selection", "evidence_required", "state", "warning"], warning_rows([{"selection_id": i, "selection": s, "evidence_required": e, "state": "SELECTION REQUIRED"} for i, s, e in selections]))

    checks = [
        ("JFX-ACC-01", "Three controlled manufacturer STEP hashes reproduce."),
        ("JFX-ACC-02", "Review STEP/GLB contains exact XM540/H101/S102 plus fixture/contact envelopes."),
        ("JFX-ACC-03", "All six nominal contact candidates touch S102 and remain at least 6.75 mm from XM540."),
        ("JFX-ACC-04", "All six keepout rules receive signed physical evidence."),
        ("JFX-ACC-05", "All twelve selections are closed by configuration-bound evidence."),
        ("JFX-ACC-06", "All twelve temporary-stack steps are executed and accepted."),
        ("JFX-ACC-07", "Qualified mechanical and metrology reviewers accept the installed fixture."),
        ("JFX-ACC-08", "A separate written authorization releases only the exact unpowered metrology session."),
        ("JFX-ACC-09", "Post-session teardown and article inspection pass."),
        ("JFX-ACC-10", "No result is promoted to build, powered-test, motion, safety or energization credit."),
    ]
    write_csv(OUT / "acceptance-matrix.csv", ["acceptance_id", "criterion", "execution_state", "result", "evidence_uri", "approver", "warning"], warning_rows([{"acceptance_id": i, "criterion": c, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""} for i, c in checks]))
    holds = [
        "Received XM540/H101/S102 identity and geometry",
        "Loose-part/thread-depth/screw-length metrology",
        "All twelve fixture and temporary-stack selections",
        "Qualified fixture geometry/load/datum/uncertainty review",
        "Fixture manufacture and dimensional first-article inspection",
        "Physical six-contact/keepout overlay on received articles",
        "Secondary restraint/tip/escape proof",
        "Signed temporary hardware/torque/reuse instruction",
        "Calibrated instruments and accepted measurement-system record",
        "Separate unpowered session authorization",
        "Executed traveler/evidence/nonconformance disposition",
        "Teardown/post-inspection/re-quarantine and qualified acceptance",
    ]
    write_csv(OUT / "open-holds.csv", ["hold_id", "hold", "state", "closure_evidence", "effect", "warning"], warning_rows([{"hold_id": f"JFX-H{i:02d}", "hold": h, "state": "OPEN", "closure_evidence": "NOT EXECUTED", "effect": "BLOCKS FIXTURE FABRICATION OR TEMPORARY ASSEMBLY/SESSION AS APPLICABLE"} for i, h in enumerate(holds, 1)]))
    status = {
        "identifier": ID, "round": "R252", "state": "REVIEW GEOMETRY / FAIL-CLOSED INSTRUCTION ONLY",
        "exact_vendor_steps": 3, "fixture_review_solids": len(fixture), "contact_candidates": 6,
        "keepout_rows": 6, "temporary_steps": 12, "selection_rows": 12, "open_holds": 12,
        "acceptance_rows": 10, "physical_article_exists": False, "fixture_buildable": False,
        "fixture_fabrication_authorized": False, "temporary_assembly_authorized": False,
        "session_authorized": False, "operations_executed": 0, "qualified_review_complete": False,
        "procurement_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "safety_credit": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nReview-only fixture geometry and fail-closed temporary-stack instruction. All physical selections, reviews and authority remain open.\n", encoding="utf-8")
    names = ["source-binding.csv", "contact-zone-register.csv", "keepout-register.csv", "temporary-stack-instruction.csv", "selection-register.csv", "open-holds.csv", "acceptance-matrix.csv"]
    for path in OUT.iterdir():
        if path.is_file() and path.name != "file-manifest.csv":
            shutil.copy2(path, REL / path.name)
    (REL / "index.html").write_text(guide_page(REL, names), encoding="utf-8")
    manifest(OUT)
    manifest(REL)


def build_config() -> None:
    for directory in (CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
        shutil.copytree(OLD, directory)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-36", "role": "zero-energy joint-stack fixture and temporary assembly candidate", "identifier": ID, "source_path": "release/hr-v0/joint-stack-fixture-p0.1/package-status.json", "configuration_state": "CURRENT REVIEW-ONLY FIXTURE/INSTRUCTION CANDIDATE", "release_boundary": "fixture is not buildable; all selections, physical evidence, qualified review and session authority remain open", "warning": WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id": "SUP-23", "prior_identifier": "HR-V0-CONFIG-REC-P0.15", "current_or_required_successor": CID, "disposition": "SUPERSEDED BY R252 CONFIGURATION RECORD ONLY", "use_authorized": "NO", "warning": WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    gate_impact, fields = read_csv(CFG / "gate-impact.csv")
    for row in gate_impact:
        if row["gate_id"] in {"EG-002", "EG-005", "EG-006"}:
            row["evidence_added"] += f"; {ID} exact-source review geometry, contact/keepout screen and fail-closed temporary-stack instruction"
            row["remaining_evidence"] += "; received parts; selected fixture material/contact force/restraint/hardware/tolerances; fixture FAI; physical fit/keepout proof; accepted uncertainty; signed temporary hardware instruction; separate unpowered-session authorization; executed records and qualified disposition"
    write_csv(CFG / "gate-impact.csv", fields, gate_impact)
    holds, fields = read_csv(CFG / "open-holds.csv")
    for index, hold in enumerate(("Received joint article geometry and inventory", "Fixture selections and qualified design review", "Fixture fabrication/FAI/physical keepout proof", "Temporary hardware/torque/reuse instruction", "Separate unpowered session authorization and execution"), 66):
        holds.append({"hold_id": f"HOLD-{index}", "hold": hold, "state": "NOT EXECUTED", "closure_evidence": "Signed configuration-bound evidence", "warning": WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for index, criterion in enumerate(("R252 source geometry and contact screen accepted", "R252 fixture selections accepted", "R252 fixture FAI/received fit accepted", "R252 temporary assembly instruction accepted", "R252 unpowered execution and teardown accepted", "R252 qualified disposition completed"), 98):
        acceptance.append({"acceptance_id": f"ACC-{index:02d}", "criterion": criterion, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier": CID, "round": "R252", "current_records": 36, "supersession_records": 23, "open_holds": 70, "acceptance_rows": 103, "joint_stack_fixture": ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR252 adds the review-only zero-energy fixture and temporary-stack instruction. Seventy holds and 103 unexecuted acceptances remain.\n", encoding="utf-8")
    hashes = []
    for row in current:
        path = ROOT / row["source_path"]
        hashes.append({"source_path": row["source_path"], "sha256": sha(path), "role": row["role"], "warning": WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path", "sha256", "role", "warning"], hashes)
    manifest(CFG)
    for path in CFG.iterdir():
        if path.is_file() and path.name != "file-manifest.csv":
            shutil.copy2(path, CFGR / path.name)
    names = ["current-configuration-map.csv", "supersession-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv"]
    (CFGR / "index.html").write_text(guide_page(
        CFGR,
        names,
        identifier=CID,
        heading="Configuration reconciliation P0.16",
        lede="R252 current-source, supersession, gate-impact, hold and acceptance records.",
        status="FIXTURE NOT BUILDABLE &middot; CONFIGURATION NOT AUTHORIZED FOR WORK &middot; ALL ACCEPTANCES OPEN",
        include_model=False,
    ), encoding="utf-8")
    manifest(CFGR)


def main() -> int:
    build_package()
    build_config()
    print("Generated R252 fixture candidate and P0.16: no fabrication, temporary assembly or session authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
