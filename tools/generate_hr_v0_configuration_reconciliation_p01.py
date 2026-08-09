"""Generate the R163 carrier-integrated configuration reconciliation package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration" / "hr-v0-config-reconciliation-p0.1"
OUT = ROOT / "release" / "hr-v0" / "configuration-reconciliation-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    return row | {"warning": WARNING}


def rows() -> dict[str, list[dict[str, object]]]:
    current = [
        ("CFG-01", "system electrical schematic", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/project-button-v3-p1.15-carrier-candidate.kicad_pro", "CURRENT CANDIDATE", "native ERC 0/0; physical pins, ratings and application evidence remain open"),
        ("CFG-02", "actuator star board", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pro", "CURRENT CANDIDATE", "native ERC/DRC 0/0 and source-bound P0.2 CAM review exist; supplier/process/physical release remains absent"),
        ("CFG-03", "branch current-limiter carrier", "HR-V0-DXL-PROT-CARRIER-P0.3", "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/hr-v0-dxl-protection-carrier-p0.3.kicad_pro", "CURRENT CANDIDATE", "native ERC/DRC 0/0; provider, process, FAI and physical evidence absent"),
        ("CFG-04", "carrier harness", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "release/hr-v0/dxl-protection-carrier-harness-p0.1/package-status.json", "CURRENT CANDIDATE", "source/star terminations and exact cut lengths remain selection required"),
        ("CFG-05", "carrier integration", "HR-V0-DXL-CARRIER-INTEGRATION-P0.1", "release/hr-v0/dxl-carrier-integration-p0.1/package-status.json", "CURRENT CANDIDATE", "route screens are analytical and require R162 placement reconciliation"),
        ("CFG-06", "carrier mounting interface", "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1", "release/hr-v0/dxl-carrier-mount-p0.1/package-status.json", "CURRENT CANDIDATE", "center candidates only; do not drill"),
        ("CFG-07", "system BOM", "HR-V0-BOM-P0.1", "bom/bom.csv", "CURRENT CLOSURE REGISTER", "91 groups; not a procurement release"),
        ("CFG-08", "release metadata", "HR-V0-RC-P0.1", "release/hr-v0/release-candidate.json", "CURRENT CANDIDATE", "exact accepted commit and qualified signatures absent"),
        ("CFG-09", "actuator star manufacturing review", "HR-V0-DXL-STAR-MFG-P0.2", "release/hr-v0/dxl-star-manufacturing-p0.2/package-status.json", "CURRENT REVIEW EVIDENCE", "quarantined internal CAM only; supplier/process/physical release remains absent"),
        ("CFG-10", "P1.15 watchdog/E2 parity", "HR-V0-E2-P115-PARITY-P0.1", "release/hr-v0/e2-p115-parity-p0.1/package-status.json", "CURRENT DIGITAL PARITY EVIDENCE", "69 unchanged refs and 263 terminals at exact parity; independent acceptance and all physical evidence remain absent"),
        ("CFG-11", "control-only hardware slice", "HR-V0-E2-HW-P0.4", "release/hr-v0/e2-hardware-p0.4/e2-hardware-summary.json", "CURRENT FAIL-CLOSED CANDIDATE", "P1.15-bound; actuator source/branches absent or unwired; run not authorized"),
    ]
    current_rows = [warned({"record_id": a, "role": b, "identifier": c, "source_path": d, "configuration_state": e, "release_boundary": f}) for a,b,c,d,e,f in current]

    superseded = [
        ("SUP-01", "Project Button Electrical V3-P1.14", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "historical/compatibility source; does not contain the inserted carrier interfaces"),
        ("SUP-02", "DXL-STAR-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "historical topology source; terminal names differ at the limited outputs"),
        ("SUP-03", "HR-V0-DXL-STAR-MFG-P0.1", "SELECTION REQUIRED", "historical P0.1 CAM; prohibited for fabrication of P0.2"),
        ("SUP-04", "PCB-P0.9 / HR-V0-WD-CAM-P0.1 P1.14 compatibility hold", "HR-V0-E2-P115-PARITY-P0.1", "digital P1.15 parity proved; supplier-normalized data, process acceptance and physical evidence remain open"),
        ("SUP-05", "HR-V0-E2-HW-P0.3", "HR-V0-E2-HW-P0.4", "P1.14-bound slice superseded by a P1.15-bound fail-closed slice; no run authorization"),
    ]
    superseded_rows = [warned({"record_id": a, "prior_identifier": b, "current_or_required_successor": c, "disposition": d, "use_authorized": "NO"}) for a,b,c,d in superseded]

    bom = [
        ("BOM-035", "integrated injection function", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "integrated_candidate"),
        ("BOM-051", "actuator star PCB", "DXL-STAR-P0.2-CARRIER-CANDIDATE / HR-V0-DXL-STAR-MFG-P0.2", "exact_candidate_hold"),
        ("BOM-087", "three limiter carrier PCBAs", "HR-V0-DXL-PROT-CARRIER-P0.3", "exact_candidate_hold"),
        ("BOM-088", "three carrier input harnesses", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "design_required"),
        ("BOM-089", "three carrier output harnesses", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "design_required"),
        ("BOM-090", "twelve carrier standoffs", "Essentra TNM3-6.5-10-1", "exact_candidate_hold"),
        ("BOM-091", "twenty-four carrier screws", "Essentra 0120070000VR", "exact_candidate_hold"),
    ]
    bom_rows = [warned({"item_id": a, "role": b, "bound_identifier": c, "closure_class": d, "physical_evidence": "OPEN", "procurement_released": "NO"}) for a,b,c,d in bom]

    gates = [
        ("EG-002", "configuration", "partial", "accepted immutable commit, clean-clone reproduction and qualified configuration acceptance"),
        ("EG-003", "BOM", "partial", "remaining exact selections, supplier/process evidence, received inspection and signed release"),
        ("EG-004", "electrical", "partial", "P1.15/P0.2 current CAM, physical terminals, ratings, wiring, test and qualified review"),
        ("EG-014", "branch protection", "partial", "carrier PCBA manufacture, characterization, fault/thermal/EMC evidence and acceptance"),
        ("EG-015", "harness and installation", "partial", "source/star terminations, cut lengths, routing, crimp/pull/continuity evidence and fit"),
    ]
    gate_rows = [warned({"gate_id": a, "domain": b, "status": c, "evidence_added": "HR-V0-CONFIG-REC-P0.1", "remaining_evidence": d, "gate_closed": "NO"}) for a,b,c,d in gates]

    holds = [
        ("HOLD-01", "P0.2 CAM supplier/process acceptance, normalized XYRS, DFM and first article", "OPEN"),
        ("HOLD-02", "Watchdog PCB-P0.9 supplier-normalized manufacturing package, provider/process acceptance and first article", "SELECTION REQUIRED"),
        ("HOLD-03", "E2 received physical configuration, continuity/isolation/no-backfeed evidence and four-role authorization", "NOT EXECUTED"),
        ("HOLD-04", "Limiter-carrier provider, process, stackup acceptance and first article", "SELECTION REQUIRED"),
        ("HOLD-05", "Carrier input-harness source-side terminals and exact cut lengths", "SELECTION REQUIRED"),
        ("HOLD-06", "Carrier output-harness star-side terminals and exact cut lengths", "SELECTION REQUIRED"),
        ("HOLD-07", "Received panel, board, standoff, screw and connector fit", "NOT EXECUTED"),
        ("HOLD-08", "Branch protection current-limit, reverse-energy, transient, thermal and fault characterization", "NOT EXECUTED"),
        ("HOLD-09", "Complete configuration review by qualified electrical, mechanical and functional-safety reviewers", "SELECTION REQUIRED"),
        ("HOLD-10", "Separate written work authorization for each physical stage", "NOT AUTHORIZED"),
    ]
    hold_rows = [warned({"hold_id": a, "hold": b, "state": c, "closure_evidence": "controlled record with exact article identity, method, result, reviewer and approval"}) for a,b,c in holds]

    acceptance = [warned({"acceptance_id": f"ACC-{i:02d}", "criterion": text, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}) for i, text in enumerate([
        "Current product identifiers match release metadata, BOM and handoff",
        "P1.15 system schematic reproduces native ERC 0 errors and 0 warnings",
        "P0.2 star board reproduces native ERC/DRC 0 errors and 0 warnings",
        "P0.3 carrier reproduces native ERC/DRC 0 errors and 0 warnings",
        "P0.1 star CAM is demonstrably excluded from P0.2 fabrication use",
        "All 91 BOM groups have reviewed closure classes and evidence",
        "EG-002, EG-003, EG-004, EG-014 and EG-015 remain fail-closed until their evidence is accepted",
        "Qualified reviewers accept the exact configuration and a distinct authority releases only the named next stage",
    ], 1)]
    return {
        "current-configuration-map.csv": current_rows,
        "supersession-map.csv": superseded_rows,
        "bom-integration-map.csv": bom_rows,
        "gate-impact.csv": gate_rows,
        "open-holds.csv": hold_rows,
        "acceptance-matrix.csv": acceptance,
    }


def html() -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-V0 configuration reconciliation</title><style>:root{{--ink:#0b2447;--blue:#0f5fa8;--sky:#dff3ff;--gold:#f6bd16;--paper:#f8fbff;--line:#87bde1}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.25vw,19px)/1.5 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:24px max(20px,5vw)}}main{{max-width:1160px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.05}}h2{{font-size:clamp(25px,3vw,36px)}}.warn{{background:#fff2bd;color:#4a3300;border:3px solid var(--gold);padding:16px;font-weight:800}}.flow{{display:grid;grid-template-columns:repeat(6,minmax(160px,1fr));gap:14px;overflow-x:auto;padding:8px 0}}.node{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;min-height:165px}}.node.current{{border-color:var(--blue);box-shadow:0 5px 0 #b9def5}}.arrow{{color:var(--blue);font-size:28px;font-weight:900}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;vertical-align:top;padding:12px;border:1px solid var(--line)}}th{{background:var(--sky)}}.badge{{display:inline-block;background:var(--gold);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}a{{color:#07599b}}@media(max-width:760px){{.flow{{grid-template-columns:1fr}}th,td{{display:block}}tr{{display:block;margin-bottom:16px;border-top:2px solid var(--line)}}}}</style></head><body><header><div class='warn'>{WARNING}</div><h1>One carrier-integrated candidate</h1><p>R163 reconciles the carrier-aware chain. R164 adds current P0.2 CAM review evidence. R165 proves exact P1.15 digital parity for the unchanged watchdog/E2 subset and issues a fail-closed P0.4 E2 slice. No round claims that the physical machine exists or is safe to power.</p></header><main><h2>Current configuration chain</h2><div class='flow'><div class='node current'><span class='badge'>System</span><h3>V3-P1.15</h3><p>Connected carrier-aware schematic. ERC 0/0 is connectivity evidence only.</p></div><div class='node current'><span class='badge'>Star</span><h3>P0.2</h3><p>Internal CAM review exists. Supplier/process release is absent.</p></div><div class='node current'><span class='badge'>Protection</span><h3>3 x P0.3</h3><p>J1/J2/G1 variants. No physical article or characterization.</p></div><div class='node current'><span class='badge'>Harness</span><h3>3 in + 3 out</h3><p>Several terminations and all cut lengths remain open.</p></div><div class='node current'><span class='badge'>Mounting</span><h3>12 points</h3><p>Center candidates only. Do not drill.</p></div><div class='node current'><span class='badge'>E2</span><h3>P0.4</h3><p>P1.15-bound and fail-closed. Actuator source and branches remain absent or unwired.</p></div></div><h2>What changed</h2><table><tr><th>Before</th><th>Now</th><th>Boundary</th></tr><tr><td>Release metadata named P1.14 and DXL-STAR-P0.1.</td><td>P1.15, P0.2 and P0.3 carrier chain are the current candidate.</td><td>P1.14/P0.1 remain historical review evidence.</td></tr><tr><td>System BOM stopped at 86 groups.</td><td>91 groups include carrier PCBAs, harness groups and mounting hardware.</td><td>21 groups still require selection; no procurement release.</td></tr><tr><td>Current P0.2 CAM was absent.</td><td>R164 provides source-bound internal CAM and parity records.</td><td>No supplier-normalized XYRS, provider/process acceptance, fabrication or physical evidence.</td></tr><tr><td>PCB-P0.9 and E2 P0.3 were P1.14 compatibility holds.</td><td>R165 proves 69 unchanged refs and 263 terminals at exact P1.15 parity; E2 P0.4 is current.</td><td>Independent acceptance, received construction, tests and authorization remain open.</td></tr></table><h2>Gate effect</h2><p>EG-002, EG-003, EG-004, EG-014 and EG-015 remain <strong>partial</strong>. Configuration, CAM and digital parity are necessary evidence, not proof of manufacturability, wiring, ratings, stopping performance, physical fit, or functional safety.</p><h2>Controlled records</h2><p><a href='current-configuration-map.csv'>Current map</a> &middot; <a href='supersession-map.csv'>Supersession map</a> &middot; <a href='bom-integration-map.csv'>BOM integration</a> &middot; <a href='gate-impact.csv'>Gate impact</a> &middot; <a href='open-holds.csv'>Open holds</a> &middot; <a href='acceptance-matrix.csv'>Acceptance matrix</a></p><div class='warn'>No procurement, fabrication, assembly, connection, motion or energization authority is issued.</div></main></body></html>"""


def main() -> None:
    data = rows()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, values in data.items():
            write_csv(directory / name, values)
        readme = f"# HR-V0 configuration reconciliation P0.1\n\n> **{WARNING}**\n\nR163-R165 bind the carrier-integrated P1.15 candidate, watchdog manufacturing package P0.2, watchdog CAM review P0.1, and the P1.15-bound E2 hardware slice P0.4 into one fail-closed configuration. The P1.14 record is retained as the controlled digital-parity source; superseded integration records remain historical evidence. Physical evidence and qualified acceptance remain open.\n"
        (directory / "README.md").write_text(readme, encoding="utf-8")
        status = {
            "identifier": "HR-V0-CONFIG-REC-P0.1", "round": "R163+R164+R165-SYNCHRONIZED", "date": "2026-08-09",
            "current_electrical_identifier": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "system_bom_groups": 91, "current_records": 11, "supersession_records": 5,
            "bom_integration_records": 7, "gate_records": 5, "open_holds": 10, "acceptance_rows": 8,
            "all_acceptance_executed": False, "current_p02_cam_exists": True,
            "physical_article_exists": False, "physical_test_executed": False,
            "qualified_review_complete": False, "procurement_authorized": False,
            "fabrication_authorized": False, "assembly_authorized": False,
            "connection_authorized": False, "motion_authorized": False,
            "energization_authorized": False, "safety_credit": False, "warning": WARNING,
        }
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(html(), encoding="utf-8")
    sources = [ROOT / row["source_path"] for row in data["current-configuration-map.csv"]]
    source_rows = [warned({"source_path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p), "role": "current configuration evidence"}) for p in sources]
    for directory in (ENG, OUT):
        write_csv(directory / "source-hash-register.csv", source_rows)
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files])


if __name__ == "__main__":
    main()
