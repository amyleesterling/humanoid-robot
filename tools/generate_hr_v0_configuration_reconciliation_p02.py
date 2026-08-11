#!/usr/bin/env python3
"""Generate the R212 P0.2 reconciliation with the R211 observation chain."""

from __future__ import annotations

import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path

import generate_hr_v0_configuration_reconciliation_p01 as p01


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.2"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    return row | {"warning": WARNING}


def rows() -> dict[str, list[dict[str, object]]]:
    data = deepcopy(p01.rows())
    current = data["current-configuration-map.csv"]
    for row in current:
        row["warning"] = WARNING
        if row["record_id"] == "CFG-01":
            row["configuration_state"] = "CURRENT CORE CANDIDATE"
            row["release_boundary"] = "P1.15 remains the direct watchdog/core binding; P1.17 proves exact core parity and adds the held observation view"
    current.extend([
        warned({"record_id":"CFG-13","role":"observation-integrated system view","identifier":"V3-P1.17-OBSERVATION-P0.5-CANDIDATE","source_path":"electrical/kicad/project-button-v3-p1.17-observation-p05-candidate/project-button-v3-p1.17-observation-p05-candidate.kicad_pro","configuration_state":"CURRENT SYNCHRONIZED SYSTEM VIEW","release_boundary":"P1.15 core parity and P0.5/Pi terminal maps are machine-checked; Pi acceptance, DFM, physical and qualified evidence remain open"}),
        warned({"record_id":"CFG-14","role":"runtime observation carrier","identifier":"HR-V0-RUNTIME-OBS-CARRIER-P0.5","source_path":"electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/hr-v0-runtime-observation-carrier-p0.5.kicad_pro","configuration_state":"CURRENT CANDIDATE","release_boundary":"open-drain topology is source-bound; fourteen application/manufacturing/physical/review holds remain open"}),
        warned({"record_id":"CFG-15","role":"Pi observation carrier","identifier":"HR-V0-PI-OBS-CARRIER-P0.1","source_path":"electrical/kicad/hr-v0-pi-observation-carrier-p0.1/hr-v0-pi-observation-carrier-p0.1.kicad_pro","configuration_state":"CURRENT CANDIDATE","release_boundary":"six-net passive carrier only; stack, fit, harness, load and physical evidence remain open"}),
        warned({"record_id":"CFG-16","role":"observation field harness","identifier":"HR-V0-OBSERVATION-FIELD-HARNESS-P0.1","source_path":"electrical/harness/hr-v0-observation-field-harness-p0.1/package-status.json","configuration_state":"CURRENT CANDIDATE","release_boundary":"catalog conductors and preparation envelopes exist; all cut lengths and physical evidence remain open"}),
        warned({"record_id":"CFG-17","role":"observation compute harness","identifier":"HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1","source_path":"electrical/harness/hr-v0-observation-compute-harness-p0.1/package-status.json","configuration_state":"CURRENT CANDIDATE","release_boundary":"catalog conductors and preparation envelopes exist; all cut lengths, duct fill and physical evidence remain open"}),
    ])

    superseded = data["supersession-map.csv"]
    for row in superseded:
        row["warning"] = WARNING
    superseded.extend([
        warned({"record_id":"SUP-07","prior_identifier":"V3-P1.16-OBSERVATION-CANDIDATE","current_or_required_successor":"V3-P1.17-OBSERVATION-P0.5-CANDIDATE","disposition":"historical R206 view bound the superseded P0.2 observation carrier; prohibited for current fabrication or wiring review","use_authorized":"NO"}),
        warned({"record_id":"SUP-08","prior_identifier":"HR-V0-RUNTIME-OBS-CARRIER-P0.2 / P0.3 / P0.4","current_or_required_successor":"HR-V0-RUNTIME-OBS-CARRIER-P0.5","disposition":"historical observation carriers retained for audit only; P0.5 is the current open-drain candidate","use_authorized":"NO"}),
        warned({"record_id":"SUP-09","prior_identifier":"HR-V0-CONFIG-REC-P0.1","current_or_required_successor":"HR-V0-CONFIG-REC-P0.2","disposition":"historical carrier-only reconciliation superseded by the observation-bound configuration map","use_authorized":"NO"}),
    ])

    for row in data["bom-integration-map.csv"]:
        row["warning"] = WARNING
    for row in data["gate-impact.csv"]:
        row["warning"] = WARNING
        row["evidence_added"] = "HR-V0-CONFIG-REC-P0.2"
        if row["gate_id"] in {"EG-003", "EG-004", "EG-015"}:
            row["remaining_evidence"] += "; observation assemblies/harness BOM closure, Pi acceptance, DFM, exact lengths and physical verification"
    data["gate-impact.csv"].extend([
        warned({"gate_id":"EG-010","domain":"compute power","status":"partial","evidence_added":"HR-V0-CONFIG-REC-P0.2","remaining_evidence":"Raspberry Pi 5 3V3 header-load and RP1 DC acceptance; STANDBY/ramp/brownout/back-power measurements; qualified review","gate_closed":"NO"}),
        warned({"gate_id":"EG-012","domain":"diagnostic safety boundary","status":"partial","evidence_added":"HR-V0-CONFIG-REC-P0.2","remaining_evidence":"qualified fault/CCF review and physical fault injection proving the zero-credit observation path cannot impair credited E-stop or restart prevention","gate_closed":"NO"}),
    ])

    holds = data["open-holds.csv"]
    for row in holds:
        row["warning"] = WARNING
    holds.extend([
        warned({"hold_id":"HOLD-11","hold":"Independent P1.15-to-P1.17 core-parity and P0.5 integration review","state":"SELECTION REQUIRED","closure_evidence":"qualified review disposition tied to exact commit and native sources"}),
        warned({"hold_id":"HOLD-12","hold":"Raspberry Pi 5/RP1 GPIO and 3V3 loading acceptance plus STANDBY/ramp/brownout evidence","state":"SELECTION REQUIRED","closure_evidence":"manufacturer disposition and controlled physical measurements"}),
        warned({"hold_id":"HOLD-13","hold":"P0.5 fabricator/assembler DFM, received identity, first article and fault/thermal/EMC evidence","state":"NOT EXECUTED","closure_evidence":"provider responses, inspection records and controlled test evidence"}),
        warned({"hold_id":"HOLD-14","hold":"Observation field and compute harness exact cut lengths, routing, termination and continuity/pull evidence","state":"SELECTION REQUIRED","closure_evidence":"as-built route survey, released drawings and signed physical records"}),
        warned({"hold_id":"HOLD-15","hold":"Add exact observation assemblies, hardware and harness quantities to the hierarchical BOM","state":"DESIGN REQUIRED","closure_evidence":"reviewed BOM rows with exact quantities, identities, closure classes and receiving evidence"}),
    ])

    acceptance = data["acceptance-matrix.csv"]
    for row in acceptance:
        row["warning"] = WARNING
        if row["acceptance_id"] == "ACC-01":
            row["criterion"] = "Current product identifiers match release metadata, P0.2 reconciliation and handoff"
    acceptance.extend([
        warned({"acceptance_id":"ACC-09","criterion":"P1.17 reproduces all P1.15 core components and terminal mappings and adds only OBS1/PIOBS1","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}),
        warned({"acceptance_id":"ACC-10","criterion":"P1.17 OBS1 terminal map and source hashes match current P0.5","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}),
        warned({"acceptance_id":"ACC-11","criterion":"P1.17 PIOBS1 selected terminals match the passive Pi carrier and omitted Pi positions remain no-copper","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}),
        warned({"acceptance_id":"ACC-12","criterion":"Observation assemblies and harnesses receive independent electrical, DFM and physical acceptance before any work release","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}),
    ])
    return data


def html() -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-V0 configuration P0.2</title><style>:root{{--ink:#08264a;--blue:#1167a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f7fbff;--line:#85bde2}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:24px max(20px,5vw)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.06}}h2{{font-size:clamp(25px,3vw,36px)}}.warn{{background:#fff1b8;color:#402d00;border:3px solid var(--gold);padding:16px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px}}.badge{{display:inline-block;background:var(--gold);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:12px;border:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--sky)}}a{{color:#07599b}}@media(max-width:700px){{th,td{{display:block}}tr{{display:block;margin-bottom:16px}}}}</style></head><body><header><div class='warn'>{WARNING}</div><h1>Current configuration: P1.15 core + P1.17 observation view</h1><p>R212 binds the corrected P0.5 open-drain observation carrier without changing the direct watchdog/core P1.15 boundary.</p></header><main><h2>Controlled chain</h2><div class='grid'><article class='card'><span class='badge'>Core</span><h3>Electrical P1.15</h3><p>Direct watchdog and actuator-distribution binding retained.</p></article><article class='card'><span class='badge'>System view</span><h3>Electrical P1.17</h3><p>All P1.15 core records plus OBS1 and PIOBS1. Native ERC 0/0.</p></article><article class='card'><span class='badge'>Receiver</span><h3>Observation P0.5</h3><p>Open-drain G07 stages; Pi acceptance and fourteen holds remain open.</p></article><article class='card'><span class='badge'>Pi</span><h3>Passive carrier P0.1</h3><p>Only six selected header nets; physical fit and loading remain open.</p></article><article class='card'><span class='badge'>Harnesses</span><h3>Field + compute P0.1</h3><p>Catalog candidates exist; every cut length remains selection required.</p></article></div><h2>Configuration effect</h2><table><tr><th>Corrected</th><th>Still open</th></tr><tr><td>P1.16 and observation-carrier P0.2 are no longer current. P1.17 binds P0.5 and exact Pi-carrier terminal maps with hash-level provenance.</td><td>Pi DC limits, DFM, BOM additions, cut lengths, physical routing, first article, fault/thermal/EMC tests and qualified acceptance.</td></tr></table><h2>Records</h2><p><a href='current-configuration-map.csv'>Current map</a> · <a href='supersession-map.csv'>Supersession map</a> · <a href='gate-impact.csv'>Gate impact</a> · <a href='open-holds.csv'>Open holds</a> · <a href='acceptance-matrix.csv'>Acceptance matrix</a></p><div class='warn'>All seven affected gates remain partial. No physical work or energization is authorized.</div></main></body></html>"""


def main() -> None:
    data = rows()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, values in data.items():
            write_csv(directory / name, values)
        readme = f"# HR-V0 configuration reconciliation P0.2\n\n> **{WARNING}**\n\nR212 retains P1.15 as the direct watchdog/core binding and adds the machine-parity-checked P1.17 system view, current observation carrier P0.5, Pi carrier P0.1 and both observation harness candidates. P1.16, observation P0.2/P0.3/P0.4 and configuration P0.1 are historical. Pi acceptance, BOM closure, DFM, physical evidence and qualified acceptance remain open.\n"
        (directory / "README.md").write_text(readme, encoding="utf-8")
        status = {
            "identifier":"HR-V0-CONFIG-REC-P0.2", "round":"R212", "date":"2026-08-10",
            "current_core_electrical_identifier":"Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "current_system_view_identifier":"V3-P1.17-OBSERVATION-P0.5-CANDIDATE",
            "system_bom_groups":91, "current_records":17, "supersession_records":9,
            "bom_integration_records":7, "gate_records":7, "open_holds":15, "acceptance_rows":12,
            "all_acceptance_executed":False, "physical_article_exists":False,
            "physical_test_executed":False, "qualified_review_complete":False,
            "procurement_authorized":False, "fabrication_authorized":False,
            "assembly_authorized":False, "connection_authorized":False,
            "powered_testing_authorized":False, "motion_authorized":False,
            "energization_authorized":False, "safety_credit":False, "warning":WARNING,
        }
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(html(), encoding="utf-8")
    sources = [ROOT / str(row["source_path"]) for row in data["current-configuration-map.csv"]]
    source_rows = [warned({"source_path":path.relative_to(ROOT).as_posix(), "sha256":digest(path), "role":"current configuration evidence"}) for path in sources]
    for directory in (ENG, OUT):
        write_csv(directory / "source-hash-register.csv", source_rows)
        files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path":path.name,"bytes":path.stat().st_size,"sha256":digest(path)} for path in files])


if __name__ == "__main__":
    main()
