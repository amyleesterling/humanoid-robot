#!/usr/bin/env python3
"""Generate the R245 firmware-to-mechanical source binding evidence."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "configuration/hr-v0-firmware-mechanical-source-binding-p0.1"
OUT = ROOT / "release/hr-v0/firmware-mechanical-source-binding-p0.1"
MANIFEST = SRC / "source-binding-manifest.json"
CFG_IN = ROOT / "configuration/hr-v0-config-reconciliation-p0.8"
CFG_SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.9"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.9"
IDENT = "HR-V0-FW-MECH-SRC-BIND-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.9"
MANIFEST_SHA = "5adc34ff41f2f84b1d8cf60e2a95b6f93ebc8eba1f2ac6b93642dd429b237c8a"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing headerless CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def put(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def main() -> None:
    if digest(MANIFEST) != MANIFEST_SHA:
        raise ValueError("mechanical source-binding manifest hash differs")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["identifier"] != IDENT or manifest["custom_part_manufacturing_revision"] != "HR-V0-MECH-BOM-BIND-P0.3":
        raise ValueError("mechanical source-binding identity differs")
    checks = []
    for row in manifest["sources"]:
        path = ROOT / row["path"]
        actual = digest(path) if path.is_file() else "MISSING"
        checks.append({
            "source_path": row["path"],
            "expected_sha256": row["sha256"],
            "actual_sha256": actual,
            "result": "PASS" if actual == row["sha256"] else "FAIL",
            "role": row["role"],
            "warning": WARNING,
        })
    if any(row["result"] != "PASS" for row in checks):
        raise ValueError("one or more mechanical source hashes differ")

    supervisor = json.loads((ROOT / "firmware/supervisor/supervisor-config.json").read_text(encoding="utf-8"))
    actuator = json.loads((ROOT / "firmware/supervisor/actuator-config.json").read_text(encoding="utf-8"))
    bindings = []
    for owner, config in (("supervisor-config.json", supervisor), ("actuator-config.json", actuator)):
        binding = config["mechanical_limit_binding"]
        ok = (
            binding["source_binding_identifier"] == IDENT
            and binding["source_binding_manifest_sha256"] == MANIFEST_SHA
            and binding["mechanical_revision"] == manifest["mechanical_revision"]
            and binding["kinematic_basis_revision"] == manifest["kinematic_basis_revision"]
            and binding["custom_part_manufacturing_revision"] == manifest["custom_part_manufacturing_revision"]
            and binding["hard_stop_revision"] == manifest["hard_stop_revision"]
            and binding["release_state"] == "CANDIDATE-NOT-RELEASED"
            and binding["acceptance_evidence_hash"] == "SELECTION REQUIRED"
        )
        bindings.append({
            "configuration": owner,
            "configuration_id": config["configuration_id"],
            "source_binding_identifier": binding["source_binding_identifier"],
            "source_binding_manifest_sha256": binding["source_binding_manifest_sha256"],
            "source_identity_result": "PASS" if ok else "FAIL",
            "physical_acceptance_state": binding["acceptance_evidence_hash"],
            "transport_or_motion_release": "DENIED",
            "warning": WARNING,
        })
    if any(row["source_identity_result"] != "PASS" for row in bindings):
        raise ValueError("firmware mechanical binding differs")

    holds = [
        ("FMB-H01", "Successor integrated-identity shop drawings, formal datum/GD&T, title blocks and qualified drafting review"),
        ("FMB-H02", "Received MTR, FAI, exact assembly identity, mass/inertia, fit and as-built configuration evidence"),
        ("FMB-H03", "Physical hard-stop, bumper, stopping, backlash, compliance, tolerance, cable and guard evidence"),
        ("FMB-H04", "Guarded HIL acceptance record with immutable SHA-256 evidence hash"),
        ("FMB-H05", "Qualified mechanical, electrical and functional-safety disposition plus signed work authorization"),
    ]
    hold_rows = [{"hold_id": hid, "hold": hold, "state": "NOT EXECUTED", "closure_evidence": "SELECTION REQUIRED", "warning": WARNING} for hid, hold in holds]

    for directory in (SRC, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        if directory == OUT:
            put(directory / "source-binding-manifest.json", MANIFEST.read_text(encoding="utf-8"))
        write(directory / "source-hash-verification.csv", checks)
        write(directory / "firmware-binding-verification.csv", bindings)
        write(directory / "open-holds.csv", hold_rows)
        status = {
            "identifier": IDENT,
            "round": "R245",
            "date": "2026-08-11",
            "source_binding_manifest_sha256": MANIFEST_SHA,
            "source_records": len(checks),
            "source_hashes_verified": all(row["result"] == "PASS" for row in checks),
            "firmware_configurations_bound": len(bindings),
            "source_identity_complete": True,
            "physical_acceptance_hash_present": False,
            "release_state": "CANDIDATE-NOT-RELEASED",
            "open_holds": len(holds),
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
        put(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
        put(directory / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR245 binds both firmware configuration files to a SHA-256 manifest covering the current integrated P0.8 assembly, corrected P0.3 custom-part binding, inherited P0.7 kinematic basis and P0.3 hard-stop basis. The separate physical/HIL acceptance hash remains `SELECTION REQUIRED`; motion remains fail-closed.\n")

    source_rows = "".join(f"<tr><td>{html.escape(r['role'])}</td><td><code>{html.escape(r['source_path'])}</code></td><td>{r['result']}</td></tr>" for r in checks)
    hold_html = "".join(f"<li><b>{html.escape(hid)}</b> {html.escape(hold)}</li>" for hid, hold in holds)
    put(OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENT}</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:32px clamp(16px,4vw,48px)}}h1{{font-size:clamp(32px,5vw,64px);line-height:1.05}}.warning{{padding:16px;border:3px solid #9b6d00;background:#fff3c4;font-weight:800;border-radius:12px}}.card{{background:#fff;border:2px solid var(--blue);border-radius:12px;padding:20px;margin:24px 0}}.table{{overflow:auto}}table{{border-collapse:collapse;min-width:900px;width:100%}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}li{{margin:.75rem 0}}</style></head><body><header><b>R245 · {IDENT}</b><h1>The code now knows exactly which mechanical source it is refusing to run.</h1><div class="warning">{WARNING}</div></header><main><div class="card"><b>Source identity: complete.</b><p>Both firmware configurations contain the same SHA-256 manifest identity for P0.8 integrated geometry, P0.3 custom-part binding, the inherited P0.7 kinematic basis and P0.3 stop basis.</p><p><b>Physical acceptance: absent.</b> The independent acceptance hash remains <code>SELECTION REQUIRED</code>; release state remains <code>CANDIDATE-NOT-RELEASED</code>; transport and motion remain denied.</p></div><div class="table"><table><thead><tr><th>Role</th><th>Controlled path</th><th>Hash check</th></tr></thead><tbody>{source_rows}</tbody></table></div><h2>Evidence still required</h2><ol>{hold_html}</ol></main></body></html>''')
    for directory in (SRC, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])

    names = ("current-configuration-map.csv", "supersession-map.csv", "bom-integration-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv")
    cfg = {name: read(CFG_IN / name) for name in names}
    cfg["current-configuration-map.csv"].extend([
        {"record_id": "CFG-28", "role": "current custom-part manufacturing binding", "identifier": "HR-V0-MECH-BOM-BIND-P0.3", "source_path": "release/hr-v0/mechanical-bom-binding-p0.3/package-status.json", "configuration_state": "CURRENT INTEGRATED HELD DESIGN CANDIDATE", "release_boundary": "five exact one-each parts and unchanged source hashes; successor shop drawings, DFM, FAI, physical evidence and qualified release open", "warning": WARNING},
        {"record_id": "CFG-29", "role": "firmware mechanical source binding", "identifier": IDENT, "source_path": "release/hr-v0/firmware-mechanical-source-binding-p0.1/package-status.json", "configuration_state": "CURRENT FAIL-CLOSED SOURCE IDENTITY", "release_boundary": "eight source hashes bound in two configurations; physical/HIL acceptance hash remains selection required", "warning": WARNING},
    ])
    cfg["supersession-map.csv"].append({"record_id": "SUP-16", "prior_identifier": "HR-V0-CONFIG-REC-P0.8", "current_or_required_successor": CFG_IDENT, "disposition": "P0.8 remains immutable R244 snapshot; P0.9 corrects the active five-part integrated identity and adds fail-closed firmware source hashes", "use_authorized": "NO", "warning": WARNING})
    for row in cfg["bom-integration-map.csv"]:
        if row["item_id"] == "BOM-027":
            row["bound_identifier"] = "HR-V0-MECH-BOM-BIND-P0.3 / HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
    for row in cfg["gate-impact.csv"]:
        if row["gate_id"] in {"EG-002", "EG-003", "EG-005", "EG-006"}:
            row["evidence_added"] = f"HR-V0-MECH-BOM-BIND-P0.3 / {IDENT}"
            row["remaining_evidence"] += "; R245 successor shop drawings/datum-GD&T/RFQ/assembly definition plus received, physical/HIL and qualified acceptance"
        row["gate_closed"] = "NO"
    for row in cfg["open-holds.csv"]:
        if row["hold_id"] == "HOLD-19":
            row["hold"] = "Physical/HIL mechanical acceptance hash for the source-bound integrated P0.8/P0.3 candidate"
            row["state"] = "NOT EXECUTED"
            row["closure_evidence"] = "accepted as-built, calibration, hard-stop, stopping, backlash/compliance/tolerance and guarded-HIL evidence with immutable SHA-256; qualified approval"
    cfg["acceptance-matrix.csv"].extend([
        {"acceptance_id": "ACC-48", "criterion": "All five P0.3 custom-part rows name the integrated P0.8 architecture and retain the fifteen prior artifact hashes", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING},
        {"acceptance_id": "ACC-49", "criterion": "Both firmware configurations bind the exact eight-record source manifest SHA-256", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING},
        {"acceptance_id": "ACC-50", "criterion": "Physical/HIL acceptance remains a separate immutable evidence hash and is not inferred from source identity", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING},
        {"acceptance_id": "ACC-51", "criterion": "Successor shop drawings, datum/GD&T, RFQ and part-specific assembly definition receive qualified acceptance", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING},
    ])
    for directory in (CFG_SOURCE, CFG_OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in cfg.items():
            write(directory / name, rows)
        status = {"identifier": CFG_IDENT, "round": "R245", "date": "2026-08-11", "current_core_electrical_identifier": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "unaccepted_panel_topology_candidate": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "current_mechanical_identifier": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "current_custom_part_binding": "HR-V0-MECH-BOM-BIND-P0.3", "firmware_mechanical_source_binding": IDENT, "system_bom_groups": 98, "current_records": 29, "supersession_records": 16, "bom_integration_records": 18, "gate_records": 11, "open_holds": 38, "acceptance_rows": 51, "all_acceptance_executed": False, "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING}
        put(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
        put(directory / "README.md", f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR245 corrects BOM-027 to `HR-V0-MECH-BOM-BIND-P0.3` and binds both firmware configurations to {IDENT}. Source identity is closed; shop-document, physical/HIL and qualified acceptance remain open. P1.15 remains current and P1.21 unaccepted.\n")
    cfg_sources = [{"source_path": row["source_path"], "sha256": digest(ROOT / row["source_path"]), "role": "current configuration evidence", "warning": WARNING} for row in cfg["current-configuration-map.csv"]]
    for directory in (CFG_SOURCE, CFG_OUT):
        write(directory / "source-hash-register.csv", cfg_sources)
    put(CFG_OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CFG_IDENT}</title><style>body{{margin:0;background:#f7fbfe;color:#082b4c;font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(32px,5vw,58px)}}.warning{{padding:16px;background:#fff3c4;border:3px solid #9b6d00;font-weight:800}}.card{{padding:18px;margin:18px 0;background:#fff;border:2px solid #1268a8;border-radius:12px}}</style></head><body><main><div class="warning">{WARNING}</div><h1>{CFG_IDENT}</h1><div class="card"><b>Mechanical identity corrected.</b><p>BOM-027 now points to P0.3 and the integrated P0.8 arm. Both firmware configurations bind the same eight-record source manifest.</p></div><div class="card"><b>Motion still denied.</b><p>The physical/HIL acceptance hash is still <code>SELECTION REQUIRED</code>. Shop drawings, DFM, FAI, received evidence and qualified acceptance remain open.</p></div></main></body></html>''')
    for directory in (CFG_SOURCE, CFG_OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENT}: {len(checks)} source hashes PASS / 2 firmware bindings PASS / physical acceptance absent")
    print(f"{CFG_IDENT}: 98 BOM groups / 29 current records / 38 open holds / no authority")


if __name__ == "__main__":
    main()
