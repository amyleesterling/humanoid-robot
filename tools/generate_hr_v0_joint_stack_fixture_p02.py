#!/usr/bin/env python3
"""Generate R253 rank-6 3-2-1 zero-energy joint-stack fixture candidate."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_joint_stack_fixture_p01 as p01  # noqa: E402

ID = "HR-V0-JOINT-STACK-FIXTURE-P0.2"
CID = "HR-V0-CONFIG-REC-P0.17"
WARNING = p01.WARNING
OUT = ROOT / "test-fixtures/hr-v0/joint-stack-fixture-p0.2"
REL = ROOT / "release/hr-v0/joint-stack-fixture-p0.2"
OLD = ROOT / "configuration/hr-v0-config-reconciliation-p0.16"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.17"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.17"
CHARACTERISTIC_LENGTH_MM = 48.0


def constraint_row(point: tuple[float, float, float], normal: tuple[float, float, float]) -> list[float]:
    r = np.array(point, dtype=float)
    n = np.array(normal, dtype=float)
    moment = np.cross(r, n) / CHARACTERISTIC_LENGTH_MM
    return [*n.tolist(), *moment.tolist()]


def corrected_fixture(parts: dict[str, cq.Shape]) -> tuple[dict[str, cq.Shape], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    # Review envelopes only. The six unilateral point contacts use a nominal
    # 3-2-1 arrangement on three mutually perpendicular external S102 faces.
    base = cq.Solid.makeBox(160, 120, 12, cq.Vector(-80, -94, -60))
    left = cq.Solid.makeBox(12, 78, 96, cq.Vector(-70, -82, -48))
    right = cq.Solid.makeBox(12, 78, 96, cq.Vector(58, -82, -48))
    bridge = cq.Solid.makeBox(116, 12, 12, cq.Vector(-58, -82, 36))
    specs = [
        ("JFX2-A1", "A", "PRIMARY", (-15.0, -51.5, -9.0), (0.0, -1.0, 0.0), (-15.0, -53.5, -9.0), "broad external S102 face Y=-51.500 mm", "Ty; Rx/Rz collectively"),
        ("JFX2-A2", "A", "PRIMARY", (15.0, -51.5, -9.0), (0.0, -1.0, 0.0), (15.0, -53.5, -9.0), "broad external S102 face Y=-51.500 mm", "Ty; Rx/Rz collectively"),
        ("JFX2-A3", "A", "PRIMARY", (0.0, -51.5, 9.0), (0.0, -1.0, 0.0), (0.0, -53.5, 9.0), "broad external S102 face Y=-51.500 mm", "Ty; Rx/Rz collectively"),
        ("JFX2-B1", "B", "SECONDARY", (-24.0, -44.5, -8.0), (-1.0, 0.0, 0.0), (-26.0, -44.5, -8.0), "left external S102 face X=-24.000 mm", "Tx; Ry collectively"),
        ("JFX2-B2", "B", "SECONDARY", (-24.0, -44.5, 8.0), (-1.0, 0.0, 0.0), (-26.0, -44.5, 8.0), "left external S102 face X=-24.000 mm", "Tx; Ry collectively"),
        ("JFX2-C1", "C", "TERTIARY", (0.0, -50.5, -16.5), (0.0, 0.0, -1.0), (0.0, -50.5, -18.5), "lower external S102 edge face Z=-16.500 mm", "Tz"),
    ]
    fixture = {
        "JFX2_BASE_REVIEW_ENVELOPE": base,
        "JFX2_LEFT_SUPPORT_REVIEW_ENVELOPE": left,
        "JFX2_RIGHT_SUPPORT_REVIEW_ENVELOPE": right,
        "JFX2_BRIDGE_REVIEW_ENVELOPE": bridge,
    }
    contacts: list[dict[str, object]] = []
    matrix_rows: list[dict[str, object]] = []
    matrix: list[list[float]] = []
    for contact_id, datum, role, point, normal, center, surface, constraint in specs:
        sphere = cq.Solid.makeSphere(2.0, cq.Vector(*center))
        fixture[f"{contact_id}_{role}_CONTACT_REVIEW_ENVELOPE"] = sphere
        row = constraint_row(point, normal)
        matrix.append(row)
        contacts.append({
            "contact_id": contact_id,
            "datum": datum,
            "role": role,
            "article_feature": surface,
            "nominal_contact_xyz_mm": ",".join(f"{v:.3f}" for v in point),
            "nominal_center_xyz_mm": ",".join(f"{v:.3f}" for v in center),
            "outward_normal_xyz": ",".join(f"{v:.3f}" for v in normal),
            "candidate_radius_mm": "2.000 REVIEW ENVELOPE",
            "nominal_s102_distance_mm": f"{sphere.distance(parts['S102']):.9f}",
            "nominal_xm540_distance_mm": f"{sphere.distance(parts['XM540']):.9f}",
            "nominal_h101_distance_mm": f"{sphere.distance(parts['H101']):.9f}",
            "s102_intersection_volume_mm3": f"{sphere.intersect(parts['S102']).Volume():.12f}",
            "xm540_intersection_volume_mm3": f"{sphere.intersect(parts['XM540']).Volume():.12f}",
            "h101_intersection_volume_mm3": f"{sphere.intersect(parts['H101']).Volume():.12f}",
            "nominal_constraint": constraint,
            "material_and_force": "SELECTION REQUIRED",
            "state": "NOMINAL CAD SCREEN ONLY - RECEIVED FIT AND QUALIFIED ACCEPTANCE REQUIRED",
        })
        matrix_rows.append({
            "contact_id": contact_id,
            "nx": f"{row[0]:.9f}", "ny": f"{row[1]:.9f}", "nz": f"{row[2]:.9f}",
            "rx_cross_n_over_L": f"{row[3]:.9f}", "ry_cross_n_over_L": f"{row[4]:.9f}", "rz_cross_n_over_L": f"{row[5]:.9f}",
            "characteristic_length_mm": f"{CHARACTERISTIC_LENGTH_MM:.3f}",
            "interpretation": "one frictionless unilateral normal constraint; preload/restraint not represented",
        })
    a = np.array(matrix, dtype=float)
    singular = np.linalg.svd(a, compute_uv=False)
    proof = {
        "identifier": ID,
        "method": "infinitesimal frictionless point-contact constraint matrix [n, (r cross n)/L]",
        "characteristic_length_mm": CHARACTERISTIC_LENGTH_MM,
        "rows": len(matrix),
        "rank": int(np.linalg.matrix_rank(a)),
        "singular_values": [float(value) for value in singular],
        "condition_number": float(np.linalg.cond(a)),
        "r252_coplanar_scheme_rank": 3,
        "claim_boundary": "rank 6 proves only nominal infinitesimal kinematic independence; unilateral seating, preload, stability, force, tolerance and physical suitability remain unproved",
        "warning": WARNING,
    }
    return fixture, contacts, matrix_rows, proof


def build_package() -> None:
    for directory in (OUT, REL):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
    parts = p01.joint_geometry()
    fixture, contacts, matrix_rows, proof = corrected_fixture(parts)
    model = {
        "EXACT_XM540_VENDOR_GEOMETRY": parts["XM540"],
        "EXACT_FR13_H101K_VENDOR_GEOMETRY": parts["H101"],
        "EXACT_FR13_S102K_VENDOR_GEOMETRY": parts["S102"],
        **fixture,
    }
    assembly = cq.Assembly(name="HR_V0_JOINT_STACK_FIXTURE_P02_NOT_RELEASED")
    for name, shape in model.items():
        if "CONTACT" in name:
            color = cq.Color(0.95, 0.70, 0.10)
        elif "JFX2_" in name:
            color = cq.Color(0.08, 0.28, 0.52)
        elif "XM540" in name:
            color = cq.Color(0.15, 0.55, 0.82)
        else:
            color = cq.Color(0.72, 0.76, 0.79)
        assembly.add(shape, name=name, color=color)
    step_path = OUT / "HR-V0_joint-stack-fixture_P0.2_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(model.values())), str(step_path))
    p01.arm.canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_joint-stack-fixture_P0.2_review.glb"))

    source_rows = []
    for source_id, label, path, date in (
        ("JFX2-SRC-01", "XM540 controlled STEP", p01.SOURCE_STEP["XM540"], "drawing date 2019-03-18; controlled 2026-08-06"),
        ("JFX2-SRC-02", "FR13-H101K controlled STEP", p01.SOURCE_STEP["H101"], "drawing date 2026-01-07; controlled 2026-08-06"),
        ("JFX2-SRC-03", "FR13-S102K controlled STEP", p01.SOURCE_STEP["S102"], "drawing date 2026-01-07; controlled 2026-08-06"),
        ("JFX2-SRC-04", "R252 superseded fixture status", ROOT / "release/hr-v0/joint-stack-fixture-p0.1/package-status.json", "R252 / 2026-08-11"),
        ("JFX2-SRC-05", "R251 first-shop-session status", ROOT / "release/hr-v0/first-shop-session-p0.1/package-status.json", "R251 / 2026-08-11"),
        ("JFX2-SRC-06", "R84 joint-stack traveler", ROOT / "test-fixtures/hr-v0/joint-stack-metrology-p0.1/operation-sequence.csv", "R84 / 2026-08-08"),
    ):
        source_rows.append({"source_id": source_id, "source": label, "path": path.relative_to(ROOT).as_posix(), "sha256": p01.sha(path), "revision_or_date": date, "use": "BOUND INPUT - DOES NOT AUTHORIZE WORK"})
    p01.write_csv(OUT / "source-binding.csv", ["source_id", "source", "path", "sha256", "revision_or_date", "use", "warning"], p01.warning_rows(source_rows))

    manufacturer = [
        {"source_id": "JFX2-MAN-01", "manufacturer": "ROBOTIS US", "url": "https://www.robotis.us/dynamixel-xm540-w270-t/", "document_revision_or_date": "live page; no formal revision exposed; checked 2026-08-11", "verified_fact": "title XM540-W270-T; SKU 902-0137-000; TTL; 12 V; 165 g; 10.6 N m stall; estimated rated torque 2.12 N m disclosed as 20 percent of stall", "conflict_or_limit": "same package table names XM540-W270-R; written supplier SKU/model/protocol confirmation remains required", "state": "CURRENT PRIMARY SOURCE - PURCHASE BLOCKED"},
        {"source_id": "JFX2-MAN-02", "manufacturer": "ROBOTIS US", "url": "https://www.robotis.us/fr13-h101k-set/", "document_revision_or_date": "live page; no formal revision exposed; checked 2026-08-11", "verified_fact": "FR13-H101K Set; SKU 903-0270-300; includes H101, I101, FWB M2.5x17, WB M2.5x5, WB M2.5x4 and spacer rings", "conflict_or_limit": "no project torque, strength class, coating, locking or reuse rule", "state": "CURRENT PRIMARY SOURCE - RECEIVING AND ENGINEERING HOLD"},
        {"source_id": "JFX2-MAN-03", "manufacturer": "ROBOTIS US", "url": "https://www.robotis.us/fr13-s102k-set/", "document_revision_or_date": "live page; no formal revision exposed; checked 2026-08-11", "verified_fact": "FR13-S102K Set; SKU 903-0269-300; bottom-side X540 frame; package fasteners and spacer rings", "conflict_or_limit": "stock/price are temporal; no project torque, strength class, coating, locking or reuse rule", "state": "CURRENT PRIMARY SOURCE - RECEIVING AND ENGINEERING HOLD"},
        {"source_id": "JFX2-MAN-04", "manufacturer": "ROBOTIS", "url": "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/", "document_revision_or_date": "live e-Manual; no formal page revision exposed; checked 2026-08-11", "verified_fact": "X540 assembly requires thrust-washer/index alignment, H101 idler/output assembly, S102 bottom assembly, spacer rings and screw lengths within published mounting depths; stall differs from continuous/real-world output", "conflict_or_limit": "page aggregates XH/XM/XD X540 data and does not publish a Project Button torque/reuse instruction", "state": "CURRENT PRIMARY SOURCE - APPLICATION ENGINEERING HOLD"},
    ]
    p01.write_csv(OUT / "manufacturer-evidence.csv", ["source_id", "manufacturer", "url", "document_revision_or_date", "verified_fact", "conflict_or_limit", "state", "warning"], p01.warning_rows(manufacturer))
    p01.write_csv(OUT / "contact-zone-register.csv", list(contacts[0].keys()) + ["warning"], p01.warning_rows(contacts))
    p01.write_csv(OUT / "constraint-matrix.csv", list(matrix_rows[0].keys()) + ["warning"], p01.warning_rows(matrix_rows))
    (OUT / "constraint-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    supersession = [{
        "prior_identifier": "HR-V0-JOINT-STACK-FIXTURE-P0.1",
        "defect": "six coplanar contacts constrain only three independent infinitesimal degrees of freedom; in-plane translation and rotation remain free",
        "disposition": "SUPERSEDED FOR LOCATING-SCHEME REVIEW - PROHIBITED FOR FIXTURE FABRICATION OR SESSION USE",
        "successor": ID,
        "successor_limit": "P0.2 is rank-6 nominal review geometry only; it remains not buildable and not authorized",
    }]
    p01.write_csv(OUT / "supersession-disposition.csv", list(supersession[0].keys()) + ["warning"], p01.warning_rows(supersession))

    keepouts = [
        ("JFX2-KO-01", "XM540 case, covers, output/idler and all actuator surfaces", "NO FIXTURE CONTACT OR LOAD"),
        ("JFX2-KO-02", "XM540 connector and connector-side recess", "NO CONTACT; NO CABLE PRESENT"),
        ("JFX2-KO-03", "H101 broad/side faces and all attachment holes", "NO FIXTURE CONTACT"),
        ("JFX2-KO-04", "S102 holes, bends, radii and unselected faces", "ONLY SIX DESIGNATED DATUM CONTACTS"),
        ("JFX2-KO-05", "hard-stop, bumper, guard, cable and service-tool regions", "NO CONTACT OR INFERRED CLEARANCE"),
        ("JFX2-KO-06", "joint swept envelope outside an accepted pose list", "NO ARTICULATION"),
        ("JFX2-KO-07", "datum B/C edge faces under preload", "NO DEFORMATION, SLIP OR BURR CONTACT"),
    ]
    p01.write_csv(OUT / "keepout-register.csv", ["keepout_id", "region", "rule", "verification", "state", "warning"], p01.warning_rows([{"keepout_id": i, "region": r, "rule": rule, "verification": "received article/fixture overlay and signed physical evidence", "state": "NOT EXECUTED"} for i, r, rule in keepouts]))

    steps = [
        ("JFX2-TMP-001", "Verify zero-energy area; exclude every power source, U2D2 and actuator cable.", "NO SOURCE-CAPABLE ITEM PRESENT", "STOP/REMOVE"),
        ("JFX2-TMP-002", "Reconcile received actuator, H101, S102, idler, washer, rings and screws to accepted inventory.", "EXACT IDENTITIES AND CONDITION", "QUARANTINE/NCR"),
        ("JFX2-TMP-003", "Complete loose-part, thread-depth and screw-length metrology before threaded assembly.", "ACCEPTED RAW DATA AND UNCERTAINTY", "NO ASSEMBLY"),
        ("JFX2-TMP-004", "Obtain signed screw allocation, spacer, torque, tool, locking prohibition and reuse/disposition instruction.", "CONFIGURATION-BOUND SIGNATURE", "NO SCREW INSERTION"),
        ("JFX2-TMP-005", "Verify fixture material, tolerances, datum features, calibrated contact geometry and FAI.", "QUALIFIED FIXTURE ACCEPTANCE", "NO ARTICLE CONTACT"),
        ("JFX2-TMP-006", "Trial-fit without screws or preload; verify only A1/A2/A3/B1/B2/C1 can contact.", "PHYSICAL OVERLAY AND KEEP-OUT PASS", "REMOVE FIXTURE/NCR"),
        ("JFX2-TMP-007", "Install thrust washer and align manufacturer index marks exactly as accepted.", "PHOTOGRAPH BEFORE COVER-UP", "DISASSEMBLE/NCR"),
        ("JFX2-TMP-008", "Install temporary article stack using only the signed hardware instruction; no cable or threadlocker.", "NO BOTTOMING, GAP, DISTORTION OR RESISTANCE", "STOP/DO NOT FORCE"),
        ("JFX2-TMP-009", "Seat datum A contacts under the selected low-force method; verify three-point seating.", "A1/A2/A3 CONTACT AND FORCE ACCEPTED", "UNLOAD/REMOVE"),
        ("JFX2-TMP-010", "Translate only as instructed to seat B1/B2 without losing datum A.", "B CONTACTS SEATED; A RETAINED", "UNLOAD/REMOVE"),
        ("JFX2-TMP-011", "Seat C1 only after A/B verification; prove restraint supplies no unintended seventh locator.", "C SEATED; NO REDUNDANT HARD CONTACT", "UNLOAD/REMOVE"),
        ("JFX2-TMP-012", "Apply selected anti-lift/escape restraint and record forces; it may not become a locator or rotation stop.", "FORCE/STABILITY ACCEPTED", "NO ARTICULATION"),
        ("JFX2-TMP-013", "Execute only the signed pose/measurement list with independent continuous keepout witness.", "COMPLETE HASHED RAW RECORD", "STOP/QUARANTINE/NCR"),
        ("JFX2-TMP-014", "Unload in reverse C/B/A order, teardown, inspect every article and re-quarantine.", "NO DAMAGE/GALLING/DEBRIS/DEFORMATION", "QUARANTINE/NCR"),
    ]
    p01.write_csv(OUT / "temporary-stack-instruction.csv", ["step_id", "instruction", "acceptance", "failure_action", "execution_state", "evidence_uri", "signer", "warning"], p01.warning_rows([{"step_id": i, "instruction": text, "acceptance": ok, "failure_action": fail, "execution_state": "NOT EXECUTED", "evidence_uri": "", "signer": ""} for i, text, ok, fail in steps]))

    selections = [
        ("JFX2-SEL-01", "fixture structural material and manufacturing process", "load, stability and metrology compatibility"),
        ("JFX2-SEL-02", "six contact types/materials", "hardness, compression, friction, cleanliness and non-marring evidence"),
        ("JFX2-SEL-03", "A/B/C seating forces and sequence", "received article allowables and repeatability study"),
        ("JFX2-SEL-04", "anti-lift/escape restraint topology and force", "stability proof without redundant hard location"),
        ("JFX2-SEL-05", "fixture datum scheme, tolerances and adjustment", "qualified mechanical/metrology review"),
        ("JFX2-SEL-06", "fixture fasteners, torques, locking and reuse", "complete load path and received proof"),
        ("JFX2-SEL-07", "article screw identities and lengths", "received inventory and measured mounting depths"),
        ("JFX2-SEL-08", "spacer-ring allocation", "received inventory and manufacturer instruction reconciliation"),
        ("JFX2-SEL-09", "temporary article torque and tool", "manufacturer/qualified evidence and calibrated tool"),
        ("JFX2-SEL-10", "temporary screw reuse/disposition", "manufacturer or qualified engineering disposition"),
        ("JFX2-SEL-11", "approved pose and measurement list", "received interference/keepout review"),
        ("JFX2-SEL-12", "fixture calibration and verification method", "accepted uncertainty and repeatability evidence"),
        ("JFX2-SEL-13", "datum B/C edge-contact allowable", "received edge condition, local stress/deformation and burr inspection"),
        ("JFX2-SEL-14", "operator loading/unloading aids", "no pinch, drop, forced fit or hidden contact"),
    ]
    p01.write_csv(OUT / "selection-register.csv", ["selection_id", "selection", "evidence_required", "state", "warning"], p01.warning_rows([{"selection_id": i, "selection": text, "evidence_required": evidence, "state": "SELECTION REQUIRED"} for i, text, evidence in selections]))

    holds = [
        "Written XM540-W270-T / SKU 902-0137-000 / TTL supplier confirmation",
        "Received XM540/H101/S102 identity, condition and source parity",
        "Loose-part/thread-depth/screw-length metrology",
        "All fourteen fixture and temporary-stack selections",
        "Qualified rank-6 geometry/load/stability/datum/uncertainty review",
        "Fixture manufacture and dimensional first-article inspection",
        "Physical A/B/C contact and all keepout proof",
        "Datum B/C local deformation and edge-condition proof",
        "Anti-lift/escape stability proof without redundant location",
        "Signed temporary hardware/torque/reuse instruction",
        "Calibrated instruments and accepted measurement-system record",
        "Separate unpowered session authorization",
        "Executed traveler, teardown, NCR disposition and qualified acceptance",
    ]
    p01.write_csv(OUT / "open-holds.csv", ["hold_id", "hold", "state", "closure_evidence", "effect", "warning"], p01.warning_rows([{"hold_id": f"JFX2-H{i:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED", "effect": "BLOCKS PURCHASE, FIXTURE FABRICATION OR TEMPORARY ASSEMBLY/SESSION AS APPLICABLE"} for i, hold in enumerate(holds, 1)]))

    criteria = [
        "All six controlled source hashes reproduce.",
        "P0.1 is visibly superseded and prohibited for fixture fabrication/session use.",
        "Review STEP/GLB contains exact XM540/H101/S102 plus four structural and six contact envelopes.",
        "All six contacts are tangent to intended nominal S102 faces with zero modeled penetration and remain clear of nominal XM540/H101.",
        "Normalized six-row frictionless contact matrix has rank 6.",
        "Qualified reviewer accepts contact locations, condition number and unilateral/preload interpretation.",
        "All seven keepouts receive signed physical evidence.",
        "All fourteen selections close with configuration-bound evidence.",
        "Fixture FAI and received-article A/B/C fit/stability evidence pass.",
        "All fourteen temporary-stack steps execute and pass.",
        "Separate written authorization releases only the exact unpowered metrology session.",
        "Teardown passes and no result is promoted to powered, motion, safety or energization credit.",
    ]
    p01.write_csv(OUT / "acceptance-matrix.csv", ["acceptance_id", "criterion", "execution_state", "result", "evidence_uri", "approver", "warning"], p01.warning_rows([{"acceptance_id": f"JFX2-ACC-{i:02d}", "criterion": criterion, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""} for i, criterion in enumerate(criteria, 1)]))

    status = {
        "identifier": ID, "round": "R253", "state": "RANK-6 NOMINAL 3-2-1 REVIEW GEOMETRY ONLY",
        "supersedes": "HR-V0-JOINT-STACK-FIXTURE-P0.1",
        "r252_scheme_prohibited_for_fixture_fabrication": True,
        "exact_vendor_steps": 3, "fixture_review_solids": len(fixture), "contact_candidates": 6,
        "constraint_matrix_rank": proof["rank"], "constraint_condition_number": proof["condition_number"],
        "manufacturer_evidence_rows": 4, "keepout_rows": 7, "temporary_steps": 14,
        "selection_rows": 14, "open_holds": 13, "acceptance_rows": 12,
        "physical_article_exists": False, "fixture_buildable": False, "fixture_fabrication_authorized": False,
        "temporary_assembly_authorized": False, "session_authorized": False, "operations_executed": 0,
        "qualified_review_complete": False, "procurement_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nRank-6 nominal 3-2-1 review geometry. P0.1 is superseded for locating-scheme review. P0.2 remains not buildable and not authorized.\n", encoding="utf-8")
    names = ["supersession-disposition.csv", "source-binding.csv", "manufacturer-evidence.csv", "contact-zone-register.csv", "constraint-matrix.csv", "keepout-register.csv", "temporary-stack-instruction.csv", "selection-register.csv", "open-holds.csv", "acceptance-matrix.csv"]
    for path in OUT.iterdir():
        if path.is_file() and path.name != "file-manifest.csv":
            shutil.copy2(path, REL / path.name)
    (REL / "index.html").write_text(p01.guide_page(
        REL, names, identifier=ID,
        heading="Rank-6 3-2-1 joint-stack fixture candidate",
        lede="R253 corrects the underconstrained R252 coplanar locating scheme while retaining every physical and authorization hold.",
        status="P0.1 SUPERSEDED &middot; P0.2 NOT BUILDABLE &middot; NO PURCHASE, ASSEMBLY, POWER OR MOTION",
        include_model=True,
    ).replace("HR-V0_joint-stack-fixture_P0.1_review.glb", "HR-V0_joint-stack-fixture_P0.2_review.glb"), encoding="utf-8")
    p01.manifest(OUT)
    p01.manifest(REL)


def build_config() -> None:
    for directory in (CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
        shutil.copytree(OLD, directory)
    current, fields = p01.read_csv(CFG / "current-configuration-map.csv")
    fixture_row = next(row for row in current if row["identifier"] == "HR-V0-JOINT-STACK-FIXTURE-P0.1")
    fixture_row.update({"identifier": ID, "source_path": "release/hr-v0/joint-stack-fixture-p0.2/package-status.json", "configuration_state": "CURRENT RANK-6 REVIEW-ONLY FIXTURE CANDIDATE", "release_boundary": "P0.1 prohibited; P0.2 not buildable; supplier confirmation, selections, physical evidence, qualified review and session authority open"})
    p01.write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = p01.read_csv(CFG / "supersession-map.csv")
    supersession.extend([
        {"record_id": "SUP-24", "prior_identifier": "HR-V0-JOINT-STACK-FIXTURE-P0.1", "current_or_required_successor": ID, "disposition": "SUPERSEDED - COPLANAR CONTACT SCHEME PROHIBITED FOR FIXTURE FABRICATION/SESSION USE", "use_authorized": "NO", "warning": WARNING},
        {"record_id": "SUP-25", "prior_identifier": "HR-V0-CONFIG-REC-P0.16", "current_or_required_successor": CID, "disposition": "SUPERSEDED BY R253 CONFIGURATION RECORD ONLY", "use_authorized": "NO", "warning": WARNING},
    ])
    p01.write_csv(CFG / "supersession-map.csv", fields, supersession)
    gate, fields = p01.read_csv(CFG / "gate-impact.csv")
    for row in gate:
        if row["gate_id"] in {"EG-002", "EG-005", "EG-006"}:
            row["evidence_added"] += f"; {ID} rank-6 nominal 3-2-1 correction and current ROBOTIS evidence register"
            row["remaining_evidence"] += "; supplier SKU/protocol confirmation; selected preload/restraint/material/tolerances; qualified constraint/load review; fixture FAI; received fit/stability/keepout proof; executed records"
    p01.write_csv(CFG / "gate-impact.csv", fields, gate)
    holds, fields = p01.read_csv(CFG / "open-holds.csv")
    replacements = {
        "HOLD-66": "Written XM540-W270-T / SKU / TTL supplier confirmation and received identity",
        "HOLD-67": "P0.2 3-2-1 contact/preload/restraint/tolerance selections and qualified review",
        "HOLD-68": "P0.2 fixture fabrication/FAI/physical A/B/C fit and stability proof",
        "HOLD-69": "Temporary hardware/torque/reuse instruction and measurement-system acceptance",
        "HOLD-70": "Separate unpowered session authorization, execution, teardown and qualified disposition",
    }
    for row in holds:
        if row["hold_id"] in replacements:
            row["hold"] = replacements[row["hold_id"]]
    p01.write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = p01.read_csv(CFG / "acceptance-matrix.csv")
    criteria = [
        "R253 source geometry, supersession and rank-6 contact screen accepted",
        "R253 manufacturer contradiction and supplier confirmation disposition accepted",
        "R253 fixture selections/constraint/load/stability review accepted",
        "R253 fixture FAI and received A/B/C fit accepted",
        "R253 temporary instruction, measurement system and unpowered authorization accepted",
        "R253 execution, teardown and qualified disposition completed",
    ]
    for row, criterion in zip([r for r in acceptance if r["acceptance_id"] in {f"ACC-{i:02d}" for i in range(98, 104)}], criteria):
        row["criterion"] = criterion
    p01.write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier": CID, "round": "R253", "current_records": 36, "supersession_records": 25, "open_holds": 70, "acceptance_rows": 103, "joint_stack_fixture": ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR253 supersedes the rank-3 P0.1 locating scheme with rank-6 nominal P0.2. Seventy holds and 103 unexecuted acceptances remain.\n", encoding="utf-8")
    hashes = []
    for row in current:
        path = ROOT / row["source_path"]
        hashes.append({"source_path": row["source_path"], "sha256": p01.sha(path), "role": row["role"], "warning": WARNING})
    p01.write_csv(CFG / "source-hash-register.csv", ["source_path", "sha256", "role", "warning"], hashes)
    p01.manifest(CFG)
    for path in CFG.iterdir():
        if path.is_file() and path.name != "file-manifest.csv":
            shutil.copy2(path, CFGR / path.name)
    names = ["current-configuration-map.csv", "supersession-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv"]
    (CFGR / "index.html").write_text(p01.guide_page(
        CFGR, names, identifier=CID, heading="Configuration reconciliation P0.17",
        lede="R253 current-source, supersession, gate-impact, hold and acceptance records.",
        status="P0.1 FIXTURE PROHIBITED &middot; P0.2 NOT BUILDABLE &middot; CONFIGURATION NOT AUTHORIZED FOR WORK",
        include_model=False,
    ), encoding="utf-8")
    p01.manifest(CFGR)


def main() -> int:
    build_package()
    build_config()
    print("Generated R253 rank-6 3-2-1 fixture candidate and P0.17; nothing authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
