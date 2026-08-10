#!/usr/bin/env python3
"""Generate the fail-closed PCB-P0.9/BOM binding for R149."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
CAM = ROOT / "release" / "hr-v0" / "watchdog-pcb-cam-p0.2"
PARITY = ROOT / "release" / "hr-v0" / "e2-p115-parity-p0.1" / "package-status.json"
PCB = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
BINDING = ROOT / "bom" / "hr-v0-watchdog-pcb-binding.csv"
OUT = ROOT / "release" / "hr-v0" / "watchdog-pcb-bom-binding-p0.1"
IDENTIFIER = "HR-V0-WD-BOM-BIND-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assembly_status = json.loads((ASSEMBLY / "package-status.json").read_text(encoding="utf-8"))
    assembly_bom = ASSEMBLY / "board-assembly-bom.csv"
    placement = ASSEMBLY / "assembly-placement-reference.csv"
    row = {
        "binding_id": "WDBIND-001",
        "bom_item_id": "BOM-048",
        "board_id": "PCB-P0.9",
        "electrical_revision": "Project Button Electrical V3-P1.14",
        "current_system_binding": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE via HR-V0-E2-P115-PARITY-P0.1",
        "native_pcb_path": PCB.relative_to(ROOT).as_posix(),
        "native_pcb_sha256": sha256(PCB),
        "assembly_data_id": "HR-V0-WD-PCBA-DATA-P0.2",
        "assembly_bom_path": assembly_bom.relative_to(ROOT).as_posix(),
        "assembly_bom_sha256": sha256(assembly_bom),
        "placement_path": placement.relative_to(ROOT).as_posix(),
        "placement_sha256": sha256(placement),
        "populated_references": str(assembly_status["populated_references"]),
        "bom_lines": str(assembly_status["bom_lines"]),
        "mechanical_features": str(assembly_status["mechanical_features"]),
        "cam_exists_at_issue": "FALSE",
        "current_cam_review_identifier": "HR-V0-WD-CAM-P0.2",
        "current_cam_review_exists": "TRUE",
        "supplier_xyrs_exists": "FALSE",
        "fabrication_authorized": "FALSE",
        "release_state": "EXACT CANDIDATE HOLD - CURRENT CAM REVIEW EXISTS BUT IS NOT RELEASED; ASSEMBLY PROCESS ABSENT",
        "warning": WARNING,
    }
    with BINDING.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row), lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)

    sources = [
        ROOT / "bom" / "bom.csv",
        ROOT / "bom" / "hr-v0-bom-closure.csv",
        PCB,
        ASSEMBLY / "package-status.json",
        assembly_bom,
        placement,
        BINDING,
        CAM / "package-status.json",
        CAM / "cam-output-register.csv",
        PARITY,
    ]
    status = {
        "identifier": IDENTIFIER,
        "date": "2026-08-09",
        "round": "R149+R150+R166-SYNCHRONIZED",
        "bom_item_id": "BOM-048",
        "board": "PCB-P0.9 / Electrical V3-P1.15-CARRIER-CANDIDATE via HR-V0-E2-P115-PARITY-P0.1",
        "native_board_title_revision": "PCB-P0.9 / Electrical V3-P1.14",
        "assembly_data": "HR-V0-WD-PCBA-DATA-P0.2",
        "populated_references": 42,
        "bom_lines": 16,
        "mechanical_features": 4,
        "open_assembly_holds": len(read_csv(ASSEMBLY / "assembly-data-holds.csv")),
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in sources},
        "provider_selected": False,
        "provider_contacted": False,
        "files_uploaded": False,
        "supplier_normalized_xyrs_exists": False,
        "cam_exists_at_issue": False,
        "current_cam_review_identifier": "HR-V0-WD-CAM-P0.2",
        "current_cam_review_exists": True,
        "current_cam_review_released": False,
        "physical_article_exists": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    facts = [
        ("42", "populated references"),
        ("16", "exact-MPN BOM lines"),
        ("4", "separate NPTH mounting features"),
        ("10", "current Gerber/job review files; zero released"),
    ]
    cards = "".join(f'<article class="card"><div class="metric">{value}</div>{html.escape(label)}</article>' for value, label in facts)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 watchdog PCB BOM binding</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f5fbff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.3rem,5.5vw,4.8rem);line-height:1.03;max-width:18ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.7rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}.card{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}.metric{{font-size:clamp(2rem,4vw,3.5rem);font-weight:900}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:950px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code{{font-size:14px;overflow-wrap:anywhere}}a{{color:#075d98}}</style></head><body><header><div>{IDENTIFIER} &middot; issued R149 &middot; synchronized R166</div><h1>The live BOM points to watchdog board PCB-P0.9.</h1><div class="warning">{WARNING}. Historical P0.1 CAM remains controlled. Current P0.2 CAM is internal review evidence only.</div></header><main><p>BOM-048 binds the native PCB-P0.9 source to the P0.2 assembly BOM and placement reference by SHA-256. R166 adds P1.15-bound source and parity hashes without releasing the CAM outputs.</p><section class="grid">{cards}</section><div class="boundary"><h2>What the exact identity proves</h2><p>The current configuration contains one native board, 42 populated references represented by 16 exact-MPN BOM lines, 42 internal placement-reference rows, and four unpopulated mounting holes. The current CAM review package is <code>HR-V0-WD-CAM-P0.2</code>, bound to <code>HR-V0-E2-P115-PARITY-P0.1</code>. This package proves only configuration agreement.</p></div><h2>Controlled files</h2><div class="table-wrap"><table><thead><tr><th>Role</th><th>Repository path</th><th>SHA-256</th><th>Supplier use</th></tr></thead><tbody><tr><td>Native PCB</td><td><code>{html.escape(row["native_pcb_path"])}</code></td><td><code>{row["native_pcb_sha256"][:20]}&hellip;</code></td><td>INTERNAL ONLY</td></tr><tr><td>Assembly BOM</td><td><code>{html.escape(row["assembly_bom_path"])}</code></td><td><code>{row["assembly_bom_sha256"][:20]}&hellip;</code></td><td>NOT RELEASED</td></tr><tr><td>Placement reference</td><td><code>{html.escape(row["placement_path"])}</code></td><td><code>{row["placement_sha256"][:20]}&hellip;</code></td><td>NOT MACHINE XYRS</td></tr></tbody></table></div><div class="boundary"><h2>Twelve assembly holds remain open</h2><p>Supplier coordinates, reference-level DFM, sourcing/traceability, SMT and THT processes, insulation/cleanliness, Pico process, fabrication definition, first article, independent qualified review, immutable supplier packet, and separate work authorization remain open. The current CAM retains six additional CAM-specific holds.</p></div><p><a href="../../../bom/hr-v0-watchdog-pcb-binding.csv">Download the binding</a> &middot; <a href="../watchdog-pcb-cam-p0.2/index.html">Open the current CAM review guide</a></p></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: PCB-P0.9 / 42 populated references / 16 BOM lines / 4 NPTH features")
    print("BOM-048 exact candidate only; current CAM review exists but supplier release, XYRS, fabrication, assembly and energization remain false")
    print(WARNING)


if __name__ == "__main__":
    main()
