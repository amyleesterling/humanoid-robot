#!/usr/bin/env python3
"""Generate the corrected, fail-closed R213 custom-part/BOM candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAWING = ROOT / "release" / "hr-v0" / "mechanical-drawing-p0.1"
CSK = ROOT / "release" / "hr-v0" / "countersink-mbd-p0.1"
OLD_BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding.csv"
BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding-p0.2.csv"
OUT = ROOT / "release" / "hr-v0" / "mechanical-bom-binding-p0.2"
DOC = ROOT / "docs" / "hr-v0-mechanical-bom-binding-p0.2.md"
GATE = ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r213.csv"
IDENTIFIER = "HR-V0-MECH-BOM-BIND-P0.2"
ARCHITECTURE = "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
PART_IDS = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise ValueError(f"{path}: refusing to write an empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update_row(path: Path, key: str, key_value: str, updates: dict[str, str]) -> None:
    records = read_csv(path)
    if not records:
        raise RuntimeError(f"{path}: no data rows")
    unknown = set(updates) - set(records[0])
    if unknown:
        raise RuntimeError(f"{path}: update contains unknown columns: {sorted(unknown)}")
    matched = 0
    updated_record: dict[str, str] | None = None
    for record in records:
        if record.get(key) == key_value:
            record.update(updates)
            matched += 1
            updated_record = record
    if matched != 1:
        raise RuntimeError(f"{path}: expected one {key}={key_value}, found {matched}")
    assert updated_record is not None
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(records[0]), lineterminator="\n")
    writer.writerow(updated_record)
    original_lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    row_indices = [index for index, line in enumerate(original_lines) if line.startswith(f"{key_value},")]
    if len(row_indices) != 1:
        raise RuntimeError(f"{path}: expected one physical row for {key_value}, found {len(row_indices)}")
    original_lines[row_indices[0]] = buffer.getvalue()
    path.write_text("".join(original_lines), encoding="utf-8", newline="")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    old = {row["part_id"]: row for row in read_csv(OLD_BINDING)}
    source = {row["part_id"]: row for row in read_csv(DRAWING / "source-binding.csv")}
    comparison = {row["part_id"]: row for row in read_csv(CSK / "part-comparison.csv")}

    bindings: list[dict[str, object]] = []
    parity: list[dict[str, object]] = []
    for index, part_id in enumerate(PART_IDS, start=1):
        legacy = old[part_id]
        current = source[part_id]
        compare = comparison.get(part_id)
        relation = compare["external_envelope_relation"] if compare else "IDENTICAL P0.7 C05 SOURCE RETAINED"
        delta = compare["maximum_bbox_delta_mm"] if compare else "0.0"
        bindings.append({
            "binding_id": f"MBIND2-{index:03d}",
            "bom_item_id": "BOM-027",
            "architecture_id": ARCHITECTURE,
            "part_id": part_id,
            "part_name": legacy["part_name"],
            "quantity_candidate": "1",
            "material_candidate": legacy["material_candidate"],
            "process_candidate": legacy["process_candidate"],
            "step_path": current["step_path"],
            "step_sha256": current["step_sha256"],
            "dxf_path": current["finished_dxf_path"],
            "dxf_sha256": current["finished_dxf_sha256"],
            "drawing_path": current["drawing_path"],
            "drawing_sha256": current["drawing_sha256"],
            "configuration_state": "CURRENT HELD DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED",
            "quotation_authorized": "FALSE",
            "fabrication_authorized": "FALSE",
            "release_state": "EXACT CANDIDATE HOLD - DFM, FAI, PHYSICAL EVIDENCE AND QUALIFIED RELEASE REQUIRED",
            "warning": WARNING,
        })
        parity.append({
            "part_id": part_id,
            "p0_7_step_path": legacy["step_path"],
            "p0_7_step_sha256": legacy["step_sha256"],
            "p0_8_step_path": current["step_path"],
            "p0_8_step_sha256": current["step_sha256"],
            "maximum_external_bbox_delta_mm": delta,
            "external_envelope_relation": relation,
            "assembly_placement_effect": "NONE - EXTERNAL ENVELOPE AND CONTROLLED HOLE CENTERS UNCHANGED",
            "review_state": "INDEPENDENT AND QUALIFIED REVIEW OPEN",
            "warning": WARNING,
        })

    write_csv(BINDING, bindings)
    write_csv(OUT / "geometry-parity.csv", parity)
    holds = [
        ("MCP-H01", "qualified drawing/GD&T review", "Named qualified mechanical reviewer disposition of all five drawings and ICF-01"),
        ("MCP-H02", "provider DFM", "Written acceptance of exact STEP/DXF/drawing hashes and every tolerance/operation"),
        ("MCP-H03", "material", "Received 6061-T651 heat-lot MTR and finished thickness evidence"),
        ("MCP-H04", "countersink/fastener", "Received M5 lot seating, contact, flushness, gauge and residual-material evidence"),
        ("MCP-H05", "C05 column interface", "Received S102/profile/T-slot fit, engagement, torque, pullout, slip and prying proof"),
        ("MCP-H06", "C04 gripper interface", "Received H104 fit, engagement, tool access, load and proof evidence"),
        ("MCP-H07", "C06/C07 stop", "Bumper selection plus received rail/step metrology, contact, load and life evidence"),
        ("MCP-H08", "first articles", "All thirty FAI operations executed with calibrated-tool identities and accepted results"),
        ("MCP-H09", "mass properties", "Received mass, COM and inertia ledger reconciled to the full arm"),
        ("MCP-H10", "assembly fit", "Unpowered full-chain dry fit with cable/guard/service/tool clearances"),
        ("MCP-H11", "structural proof", "Accepted static, stop, fatigue and proof-test results under released load cases"),
        ("MCP-H12", "configuration acceptance", "Merged immutable baseline, clean-clone reproduction and signed configuration review"),
    ]
    hold_rows = [{
        "hold_id": hold_id,
        "subject": subject,
        "evidence_required": evidence,
        "state": "OPEN",
        "work_authority_effect": "BLOCKS QUOTATION, FABRICATION, ASSEMBLY AND MOTION RELEASE",
        "warning": WARNING,
    } for hold_id, subject, evidence in holds]
    write_csv(OUT / "open-holds.csv", hold_rows)

    update_row(ROOT / "bom" / "bom.csv", "item_id", "BOM-027", {
        "manufacturer_part_number": "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE held custom set: MV0-C01/C04/C05/C06/C07 x1 each; 6061-T651 9.525 mm nominal candidate",
        "baseline_status": "exact_candidate_hold",
        "selection_basis": "R213 replaces the P0.7 custom-part manufacturing identities with the corrected P0.8 drawing candidate: four nominal 11.30 mm x 2.90 mm 90 degree countersink STEP solids, unchanged C05, five finished DXFs, five conventional drawings, 26 drawing-explicit controls and 30 unexecuted FAI operations. Twelve P0.2 holds remain open; no provider contact, quote, purchase, fabrication, assembly, motion or energization authority.",
    })
    update_row(ROOT / "bom" / "hr-v0-bom-closure.csv", "item_id", "BOM-027", {
        "closure_class": "exact_candidate_hold",
        "order_code_state": "EXACT CANDIDATE",
        "allowed_action": "HOLD",
        "closure_basis": "R213 replaces the P0.7 custom-part manufacturing identities with the corrected P0.8 drawing candidate: four nominal 11.30 mm x 2.90 mm 90 degree countersink STEP solids, unchanged C05, five finished DXFs, five conventional drawings, 26 drawing-explicit controls and 30 unexecuted FAI operations. Twelve P0.2 holds remain open; no provider contact, quote, purchase, fabrication, assembly, motion or energization authority.",
    })

    source_paths = [
        DRAWING / "source-binding.csv",
        DRAWING / "drawing-control-coverage.csv",
        DRAWING / "inspection-coordinate-register.csv",
        DRAWING / "first-article-drawing-map.csv",
        CSK / "part-comparison.csv",
        BINDING,
        ROOT / "bom" / "bom.csv",
        ROOT / "bom" / "hr-v0-bom-closure.csv",
    ]
    source_rows = [{
        "repository_path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "use": "controlled R213 source",
        "warning": WARNING,
    } for path in source_paths]
    write_csv(OUT / "source-hash-register.csv", source_rows)
    write_csv(OUT / "supersession-map.csv", [{
        "historical_identifier": "HR-V0-MECH-BOM-BIND-P0.1 / HR-V0-ARM-ARCH-P0.7 custom-part manufacturing files",
        "current_identifier": f"{IDENTIFIER} / {ARCHITECTURE}",
        "scope": "BOM-027 custom-part STEP/DXF/drawing identity only; P0.7 system transforms and collision evidence remain the placement basis because external envelopes and hole centers are unchanged",
        "historical_use": "AUDIT ONLY - NOT CURRENT FOR CUSTOM-PART FABRICATION REVIEW",
        "warning": WARNING,
    }])
    write_csv(GATE, [{
        "gate_id": gate,
        "round": "R213",
        "evidence_added": f"{IDENTIFIER}; corrected P0.8 custom-part identity, exact file hashes, parity and open holds",
        "maturity": "source-controlled analytical/configuration evidence only",
        "status_after": "partial",
        "remaining_evidence": remaining,
        "warning": WARNING,
    } for gate, remaining in (
        ("EG-003", "Complete orderable BOM, provider/part acceptance, received evidence and signed configuration review"),
        ("EG-005", "Full assembly regeneration/acceptance, received fit, physical metrology and qualified mechanical release"),
        ("EG-006", "Provider DFM, MTR, FAI, proof tests and qualified drawing/fabrication release"),
    )])

    status = {
        "identifier": IDENTIFIER,
        "round": "R213",
        "date": "2026-08-10",
        "controlled_custom_part_candidate": ARCHITECTURE,
        "system_placement_basis": "HR-V0-ARM-ARCH-P0.7 / HR-V0-MECH-P0.6",
        "part_count": 5,
        "quantity_total": 5,
        "geometry_identity_count": 15,
        "drawing_explicit_control_count": 26,
        "fai_operation_count": 30,
        "open_hold_count": len(hold_rows),
        "maximum_external_bbox_delta_mm": 0.0,
        "current_for_qualified_design_review": True,
        "independent_review_complete": False,
        "qualified_review_complete": False,
        "provider_contacted": False,
        "quotation_authorized": False,
        "purchase_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = "".join(
        f'<article><span>{html.escape(str(row["part_id"]))}</span><h3>{html.escape(str(row["part_name"]))}</h3>'
        f'<p>Quantity 1 · {html.escape(str(row["configuration_state"]))}</p></article>' for row in bindings
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 corrected custom-part candidate</title><style>:root{{--ink:#08264a;--blue:#1167a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f7fbff;--line:#85bde2}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:24px max(20px,5vw)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.06}}h2{{font-size:clamp(25px,3vw,36px)}}.warn{{background:#fff1b8;color:#402d00;border:3px solid var(--gold);padding:16px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}article{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px}}article span{{display:inline-block;background:var(--gold);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}.boundary{{border-left:7px solid var(--gold);padding-left:16px;margin:28px 0}}a{{color:#07599b}}code{{font-size:14px;overflow-wrap:anywhere}}</style></head><body><header><div class="warn">{WARNING}</div><h1>Corrected custom-part files are now one controlled review chain.</h1><p>R213 replaces the P0.7 manufacturing identities without changing the arm's external envelopes, hole centers, transforms, or collision evidence.</p></header><main><h2>Five-part candidate</h2><div class="grid">{cards}</div><div class="boundary"><h2>What was corrected</h2><p>Four STEP solids now encode nominal 11.30 mm × 2.90 mm, 90° countersinks. C05 is unchanged. All five parts bind to finished-profile DXFs, conventional drawings, 26 explicit controls, ICF-01 inspection registration, and 30 blank FAI operations.</p></div><div class="boundary"><h2>What remains open</h2><p>Independent and qualified drawing review, provider DFM, MTR, received fastener seating, FAI, dry fit, structural and stop proof, mass properties, physical tests, and configuration acceptance. Passing repository checks is not manufacturing approval.</p></div><p><a href="../../../bom/hr-v0-mechanical-custom-part-binding-p0.2.csv">Five-row binding</a> · <a href="geometry-parity.csv">Geometry parity</a> · <a href="open-holds.csv">Open holds</a> · <a href="source-hash-register.csv">Source hashes</a> · <a href="supersession-map.csv">Supersession map</a></p><div class="warn">No provider contact, quotation, purchase, fabrication, assembly, powered test, motion, or energization is authorized.</div></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")

    DOC.write_text(f"""# HR-V0 corrected mechanical custom-part/BOM binding P0.2

> **{WARNING}**

R213 issues `{IDENTIFIER}` and makes `{ARCHITECTURE}` the current **held design candidate** for BOM-027 custom-part review. It does not release a part for quotation or machining.

The five-row binding contains one each `MV0-C01`, `MV0-C04`, `MV0-C05`, `MV0-C06`, and `MV0-C07`. Four P0.8 STEP solids replace the P0.7 upper-limit countersink model with nominal 11.30 mm × 2.90 mm, 90° geometry. C05 is unchanged. Machine evidence records zero external bounding-box delta, unchanged controlled hole centers, five finished DXFs, five conventional drawings, 26 drawing-explicit controls, five ICF-01 registrations, and 30 unexecuted FAI operations.

P0.7 remains the controlled system transform/collision basis only because the corrected solids have identical external envelopes and controlled hole centers. It is historical for BOM-027 fabrication-geometry review.

Twelve holds remain open. Independent/qualified review, provider DFM, material/MTR, received fastener seating, all FAI, unpowered fit, stop/structural proof, mass properties, configuration acceptance, and physical evidence are absent. `EG-003`, `EG-005`, and `EG-006` remain partial.
""", encoding="utf-8")

    print(f"{IDENTIFIER}: 5 parts / 15 exact file identities / 26 controls / 30 blank FAI operations")
    print("P0.7 external placement basis retained; corrected P0.8 manufacturing geometry is current for qualified review only")
    print(WARNING)


if __name__ == "__main__":
    main()
