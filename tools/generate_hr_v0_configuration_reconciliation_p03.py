#!/usr/bin/env python3
"""Generate R214 current-configuration reconciliation with integrated P0.8 mechanics."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.2"
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.3"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.3"
IDENTIFIER = "HR-V0-CONFIG-REC-P0.3"
MECHANICAL = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def warned(record: dict[str, str]) -> dict[str, str]:
    record["warning"] = WARNING
    return record


def build_data() -> dict[str, list[dict[str, str]]]:
    names = (
        "current-configuration-map.csv", "supersession-map.csv", "bom-integration-map.csv",
        "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv",
    )
    data = {name: read_csv(SOURCE / name) for name in names}

    data["current-configuration-map.csv"].append(warned({
        "record_id": "CFG-18",
        "role": "integrated mechanical arm candidate",
        "identifier": MECHANICAL,
        "source_path": "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/architecture-summary.json",
        "configuration_state": "CURRENT HELD INTEGRATED MECHANICAL CANDIDATE",
        "release_boundary": "directly imports all five R213 STEP identities at unchanged P0.7 transforms; DFM, FAI, received fit, physical proof, mass closure and qualified release remain open",
    }))

    data["supersession-map.csv"].append(warned({
        "record_id": "SUP-10",
        "prior_identifier": "HR-V0-ARM-ARCH-P0.7 / HR-V0-MECH-BOM-BIND-P0.1",
        "current_or_required_successor": f"{MECHANICAL} / HR-V0-MECH-BOM-BIND-P0.2",
        "disposition": "P0.7 remains historical analytical transform/collision basis only; P0.1 manufacturing identity is prohibited for current fabrication review",
        "use_authorized": "NO",
    }))

    data["bom-integration-map.csv"].append(warned({
        "item_id": "BOM-027",
        "role": "five custom metal arm parts",
        "bound_identifier": f"HR-V0-MECH-BOM-BIND-P0.2 / {MECHANICAL}",
        "closure_class": "exact_candidate_hold",
        "physical_evidence": "OPEN",
        "procurement_released": "NO",
    }))

    for row in data["gate-impact.csv"]:
        row["evidence_added"] = IDENTIFIER
        if row["gate_id"] == "EG-003":
            row["remaining_evidence"] += "; mechanical DFM/FAI, received identity, fit, proof and qualified release"
    data["gate-impact.csv"].extend([
        warned({"gate_id": "EG-005", "domain": "mechanical configuration", "status": "partial", "evidence_added": IDENTIFIER,
                "remaining_evidence": "qualified acceptance of exact P0.8 integration; received article identity, dimensional FAI, complete mass/inertia, fit and as-built configuration evidence", "gate_closed": "NO"}),
        warned({"gate_id": "EG-006", "domain": "collision and stop validation", "status": "partial", "evidence_added": IDENTIFIER,
                "remaining_evidence": "as-built guard/cable/tolerance/deformation collision proof, stop load and stopping-travel tests, backlash/compliance/uncertainty closure and qualified acceptance", "gate_closed": "NO"}),
    ])

    data["open-holds.csv"].extend([
        warned({"hold_id": "HOLD-16", "hold": "Independent qualified review of exact five-file P0.8 arm integration", "state": "SELECTION REQUIRED", "closure_evidence": "signed disposition tied to exact commit, binding hashes, assembly hash and checker results"}),
        warned({"hold_id": "HOLD-17", "hold": "Mechanical provider DFM, material/MTR and first-article inspection for C01/C04/C05/C06/C07", "state": "NOT EXECUTED", "closure_evidence": "provider response, received identities, material records and completed FAI traveler"}),
        warned({"hold_id": "HOLD-18", "hold": "As-built arm fit, mass/inertia, structural proof, collision, stop, cable and guard validation", "state": "NOT EXECUTED", "closure_evidence": "controlled physical test records and qualified acceptance against exact articles"}),
        warned({"hold_id": "HOLD-19", "hold": "Firmware mechanical binding and acceptance hash for the integrated P0.8 candidate", "state": "DESIGN REQUIRED", "closure_evidence": "fail-closed firmware revision with explicit inherited P0.7 kinematic basis and unresolved physical/HIL acceptance"}),
    ])

    data["acceptance-matrix.csv"].extend([
        warned({"acceptance_id": "ACC-13", "criterion": "All five integrated custom-part files are byte-identical to the R213 P0.2 binding", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}),
        warned({"acceptance_id": "ACC-14", "criterion": "P0.8 hole axes and complete transform/interface schedules match the controlled definition", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}),
        warned({"acceptance_id": "ACC-15", "criterion": "P0.8 collision, continuous-clearance and J2 stop evidence reproduce under the dedicated checker", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}),
        warned({"acceptance_id": "ACC-16", "criterion": "Physical DFM/FAI/fit/proof evidence and qualified mechanical acceptance are complete before any work release", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}),
    ])
    return data


def guide(data: dict[str, list[dict[str, str]]]) -> str:
    mechanical = next(row for row in data["current-configuration-map.csv"] if row["identifier"] == MECHANICAL)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 current configuration P0.3</title><style>
:root{{--ink:#08264a;--blue:#1167a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f7fbff;--line:#85bde2;--hold:#fff1b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--ink),#0d5a96);color:#fff;padding:30px max(20px,5vw);border-bottom:7px solid var(--gold)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(34px,5vw,60px);line-height:1.05;max-width:19ch}}h2{{font-size:clamp(26px,3vw,38px)}}h3{{font-size:21px}}.warn{{background:var(--hold);color:#402d00;border:3px solid var(--gold);padding:16px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}.card{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px}}.metric{{font-size:32px;font-weight:900;color:var(--blue)}}.badge{{display:inline-block;background:var(--gold);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}a{{color:#07599b;font-weight:700}}code{{font-size:14px;overflow-wrap:anywhere}}li{{margin:.75rem 0}}</style></head><body><header><div class="warn">{WARNING}</div><p>{IDENTIFIER} · R214</p><h1>The corrected metal parts now belong to one complete arm identity.</h1><p>P0.7 remains historical analytical evidence. The current held mechanical candidate imports all five R213-controlled STEP files and reruns the complete nominal collision and stop chain.</p></header><main><section class="grid"><article class="card"><span class="badge">Exact import</span><div class="metric">5 / 5</div><p>Custom-part hashes preserved.</p></article><article class="card"><span class="badge">Collision</span><div class="metric">40,001</div><p>Sampled arm poses regenerated.</p></article><article class="card"><span class="badge">Clearance</span><div class="metric">69</div><p>Continuous body-pair certificates.</p></article><article class="card"><span class="badge">Authority</span><div class="metric">0</div><p>Work stages authorized.</p></article></section><section><h2>Current mechanical boundary</h2><div class="card"><h3>{html.escape(mechanical["identifier"])}</h3><p>{html.escape(mechanical["release_boundary"])}</p></div></section><section><h2>Why this is still held</h2><ul><li>Repository checks are model-space evidence, not received-part inspection or physical proof.</li><li>DFM, material records, FAI, fastener seating, dry fit, mass/inertia, structural proof, cables, guards and stop testing remain open.</li><li>Firmware acceptance and qualified mechanical/configuration review remain open.</li></ul></section><section><h2>Machine-readable records</h2><p><a href="current-configuration-map.csv">Current map</a> · <a href="supersession-map.csv">Supersession</a> · <a href="bom-integration-map.csv">BOM integration</a> · <a href="gate-impact.csv">Gate impact</a> · <a href="open-holds.csv">Open holds</a> · <a href="acceptance-matrix.csv">Acceptance</a></p></section><div class="warn">EG-003, EG-005 and EG-006 remain partial. No procurement, fabrication, assembly, connection, powered testing, motion, or energization is authorized.</div></main></body></html>'''


def main() -> None:
    data = build_data()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, records in data.items():
            write_csv(directory / name, records)
        (directory / "README.md").write_text(
            f"# HR-V0 configuration reconciliation P0.3\n\n> **{WARNING}**\n\nR214 adds `{MECHANICAL}` as the current held integrated mechanical identity. It directly imports the five R213 custom-part STEP identities while retaining P0.7 only as historical transform/collision basis. All physical evidence, qualified acceptance and work authority remain open.\n",
            encoding="utf-8", newline="\n")
        status = {
            "identifier": IDENTIFIER, "round": "R214", "date": "2026-08-10",
            "current_core_electrical_identifier": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "current_system_view_identifier": "V3-P1.17-OBSERVATION-P0.5-CANDIDATE",
            "current_mechanical_identifier": MECHANICAL,
            "system_bom_groups": 91, "current_records": 18, "supersession_records": 10,
            "bom_integration_records": 8, "gate_records": 9, "open_holds": 19, "acceptance_rows": 16,
            "all_acceptance_executed": False, "physical_article_exists": False,
            "physical_test_executed": False, "qualified_review_complete": False,
            "procurement_authorized": False, "fabrication_authorized": False,
            "assembly_authorized": False, "connection_authorized": False,
            "powered_testing_authorized": False, "motion_authorized": False,
            "energization_authorized": False, "safety_credit": False, "warning": WARNING,
        }
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(data), encoding="utf-8", newline="\n")

    sources = [ROOT / row["source_path"] for row in data["current-configuration-map.csv"]]
    source_rows = [warned({"source_path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "current configuration evidence"}) for path in sources]
    for directory in (ENG, OUT):
        write_csv(directory / "source-hash-register.csv", source_rows)
        files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": path.name, "bytes": str(path.stat().st_size), "sha256": digest(path)} for path in files])


if __name__ == "__main__":
    main()
