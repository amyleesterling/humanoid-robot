#!/usr/bin/env python3
"""Generate the readable R214 release surface for the integrated P0.8 arm."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated"
OUT = ROOT / "release/hr-v0/arm-architecture-p0.8-dwg-integrated"
DOC = ROOT / "docs/hr-v0-arm-architecture-p0.8-dwg-integrated.md"
IDENTIFIER = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.loads((CAD / "architecture-summary.json").read_text(encoding="utf-8"))
    integration = rows(CAD / "controlled-custom-part-integration.csv")
    continuous = json.loads((CAD / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    stop = json.loads((CAD / "j2-positive-stop-analysis.json").read_text(encoding="utf-8"))

    evidence = [
        {"evidence_id": "ARM8-E01", "claim": "five exact R213 custom-part identities imported", "value": "5 / 5 byte-identical", "source": "controlled-custom-part-integration.csv", "maturity": "REPOSITORY VERIFIED; QUALIFIED REVIEW OPEN", "warning": WARNING},
        {"evidence_id": "ARM8-E02", "claim": "P0.7 transform/interface basis unchanged", "value": "10 transforms / 9 interfaces row-identical", "source": "transform-schedule.csv; interface-schedule.csv", "maturity": "REPOSITORY VERIFIED; PHYSICAL FIT OPEN", "warning": WARNING},
        {"evidence_id": "ARM8-E03", "claim": "sampled collision schedule regenerated", "value": "40,001 poses; 0 collisions at or below 115 deg", "source": "collision-sweep.csv", "maturity": "NOMINAL MODEL SPACE ONLY", "warning": WARNING},
        {"evidence_id": "ARM8-E04", "claim": "continuous nominal clearance regenerated", "value": f"{continuous['pair_count']} pairs / {continuous['certified_leaf_cell_count']} cells / {continuous['minimum_guaranteed_clearance_mm']:.6f} mm minimum", "source": "continuous-clearance-analysis.json", "maturity": "NOMINAL MODEL SPACE ONLY", "warning": WARNING},
        {"evidence_id": "ARM8-E05", "claim": "J2 positive-stop geometry regenerated", "value": f"{stop['nominal_metal_contact_deg']:.6f} deg nominal contact; 118 deg target", "source": "j2-positive-stop-analysis.json", "maturity": "CAD CANDIDATE; PHYSICAL STOP TEST OPEN", "warning": WARNING},
        {"evidence_id": "ARM8-E06", "claim": "nominal countersink semantics corrected", "value": "11.30 mm x 2.90 mm / 90 deg; 11.40 mm and 3.10 mm retained as independent screens", "source": "architecture-summary.json", "maturity": "DRAWING CANDIDATE; FAI OPEN", "warning": WARNING},
    ]
    write_csv(OUT / "evidence-summary.csv", evidence)

    holds = [
        ("ARM8-H01", "qualified review of exact STEP import, hole axes, transforms and model semantics"),
        ("ARM8-H02", "provider DFM and released process/material/tolerance interpretation"),
        ("ARM8-H03", "material certificate and first-article dimensional inspection"),
        ("ARM8-H04", "received fastener seating, residual thickness, fit and tool access"),
        ("ARM8-H05", "received actuator/frame/member dry fit and complete fastener-stack proof"),
        ("ARM8-H06", "complete received moving mass, center of mass and inertia closure"),
        ("ARM8-H07", "structural, joint-slip, preload, fatigue and impact proof"),
        ("ARM8-H08", "physical J2 stop load, contact, overtravel, backlash, compliance and uncertainty closure"),
        ("ARM8-H09", "as-built cables, guards, deformation and collision proof"),
        ("ARM8-H10", "firmware mechanical binding, physical acceptance hash and HIL evidence"),
        ("ARM8-H11", "qualified mechanical/configuration acceptance tied to exact commit"),
        ("ARM8-H12", "separate written authority for any provider contact, procurement or physical stage"),
    ]
    hold_rows = [{"hold_id": hold_id, "hold": hold, "state": "OPEN", "closure_evidence": "controlled article-specific record with method, result, reviewer and signed disposition", "warning": WARNING} for hold_id, hold in holds]
    write_csv(OUT / "open-holds.csv", hold_rows)

    sources = [
        CAD / "architecture-summary.json", CAD / "integration-status.json", CAD / "controlled-custom-part-integration.csv",
        CAD / "HR-V0_arm_architecture_candidate.step", CAD / "HR-V0_arm_architecture_candidate.glb",
        CAD / "collision-sweep.csv", CAD / "continuous-clearance-analysis.json", CAD / "continuous-clearance-summary.csv",
        CAD / "continuous-clearance-cells.csv", CAD / "j2-positive-stop-analysis.json", CAD / "j2-positive-stop-sweep.csv",
        ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv",
        ROOT / "tools/generate_hr_v0_arm_architecture_p08.py", ROOT / "tools/check_hr_v0_arm_architecture_p08.py",
    ]
    source_rows = [{"source_path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "R214 integrated-arm evidence", "warning": WARNING} for path in sources]
    write_csv(OUT / "source-hash-register.csv", source_rows)

    status = {
        "identifier": IDENTIFIER, "round": "R214", "date": "2026-08-10",
        "controlled_part_count": len(integration), "transform_count": 10, "interface_count": 9,
        "collision_pose_count": 40001, "continuous_pair_count": continuous["pair_count"],
        "continuous_leaf_cell_count": continuous["certified_leaf_cell_count"], "open_hold_count": len(holds),
        "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    cards = "".join(f'<article class="card"><span>{html.escape(row["evidence_id"])}</span><h3>{html.escape(row["claim"])}</h3><p class="value">{html.escape(row["value"])}</p><p>{html.escape(row["maturity"])}</p></article>' for row in evidence)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 integrated arm P0.8</title><style>:root{{--ink:#08264a;--blue:#1167a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f7fbff;--line:#85bde2;--hold:#fff1b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--sky),#fff);padding:30px max(20px,5vw);border-bottom:7px solid var(--gold)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(36px,5.5vw,66px);line-height:1.03;max-width:18ch}}h2{{font-size:clamp(26px,3vw,40px)}}h3{{font-size:21px}}.warn{{background:var(--hold);border:3px solid var(--gold);padding:16px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px}}.card span{{display:inline-block;background:var(--gold);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}.value{{font-size:22px;font-weight:850;color:var(--blue)}}a{{color:#07599b;font-weight:700}}code{{font-size:14px;overflow-wrap:anywhere}}li{{margin:.75rem 0}}</style></head><body><header><div class="warn">{WARNING}</div><p>{IDENTIFIER} · R214</p><h1>Five corrected metal parts. One complete arm model.</h1><p>The full HR-V0 arm now directly consumes the exact R213-controlled STEP files. P0.7 is retained only as the unchanged analytical transform and comparison basis.</p></header><main><section><h2>What the repository proves</h2><div class="grid">{cards}</div></section><section><h2>What it does not prove</h2><p>Model-space clearance is not as-built clearance. A clean checker does not establish material, manufacturing capability, received fit, strength, stopping performance, cable behavior, guarding, or permission to build.</p></section><section><h2>Explore the evidence</h2><p><a href="../../../cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/HR-V0_arm_architecture_candidate.glb">Interactive 3D model (GLB)</a> · <a href="../../../cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/HR-V0_arm_architecture_candidate.step">Native assembly STEP</a> · <a href="evidence-summary.csv">Evidence summary</a> · <a href="open-holds.csv">Open holds</a> · <a href="source-hash-register.csv">Source hashes</a></p></section><div class="warn">Twelve holds remain open. No procurement, fabrication, assembly, connection, powered testing, motion, or energization is authorized.</div></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    DOC.write_text(f'''# HR-V0 integrated arm architecture P0.8

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Round: `R214`

## Result

The complete arm/column candidate now directly imports all five exact STEP identities from `HR-V0-MECH-BOM-BIND-P0.2`. The P0.7 transforms and nine interface records are unchanged. The successor generation reran the 40,001-pose collision sweep, 69-pair continuous-clearance certificate and J2 positive-stop analysis.

Four corrected parts encode nominal 11.30 mm × 2.90 mm, 90-degree countersinks. The 11.40 mm diameter and 3.10 mm depth remain separate conservative inspection/calculation screens. C05 is unchanged.

The model-space evidence reproduces first nominal body contact at 121.643289 degrees, the candidate 115-degree soft limit and the candidate 118-degree metal-stop target. This does not establish physical stopping distance, load capacity, fit, tolerance accumulation, cable/guard clearance or safety performance.

## Remaining release boundary

Twelve holds in `release/hr-v0/arm-architecture-p0.8-dwg-integrated/open-holds.csv` retain qualified review, DFM, MTR, FAI, received fit, fastener seating, mass/inertia, structural proof, physical stop proof, cables/guards, firmware binding and stage-specific written authority.

Passing repository checks does not authorize provider contact, procurement, fabrication, assembly, connection, powered testing, motion, or energization.
''', encoding="utf-8", newline="\n")

    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.name, "bytes": str(path.stat().st_size), "sha256": digest(path)} for path in files])


if __name__ == "__main__":
    main()
