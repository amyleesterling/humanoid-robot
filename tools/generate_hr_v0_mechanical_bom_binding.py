#!/usr/bin/env python3
"""Generate the fail-closed P0.7 custom-part/BOM binding for R148."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1"
BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding.csv"
OUT = ROOT / "release" / "hr-v0" / "mechanical-bom-binding-p0.1"
IDENTIFIER = "HR-V0-MECH-BOM-BIND-P0.1"
ARCHITECTURE = "HR-V0-ARM-ARCH-P0.7"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
PART_IDS = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {row["part_id"]: row for row in read_csv(SOURCE / "part-register.csv")}
    geometry = read_csv(SOURCE / "geometry-file-register.csv")
    by_part: dict[str, dict[str, dict[str, str]]] = {part_id: {} for part_id in PART_IDS}
    for row in geometry:
        by_part.setdefault(row["part_id"], {})[row["artifact_role"]] = row

    rows: list[dict[str, str]] = []
    for index, part_id in enumerate(PART_IDS, start=1):
        part = parts[part_id]
        roles = by_part[part_id]
        step = roles["3D candidate"]
        dxf = roles["profile reference"]
        drawing = roles["readable control drawing"]
        rows.append({
            "binding_id": f"MBIND-{index:03d}",
            "bom_item_id": "BOM-027",
            "architecture_id": ARCHITECTURE,
            "part_id": part_id,
            "part_name": part["name"],
            "quantity_candidate": "1",
            "material_candidate": part["material_candidate"],
            "process_candidate": part["process_candidate"],
            "step_path": step["repository_path"],
            "step_sha256": step["sha256"],
            "dxf_path": dxf["repository_path"],
            "dxf_sha256": dxf["sha256"],
            "drawing_path": drawing["repository_path"],
            "drawing_sha256": drawing["sha256"],
            "quotation_authorized": "FALSE",
            "fabrication_authorized": "FALSE",
            "release_state": "EXACT CANDIDATE HOLD - QUALIFIED REVIEW AND PHYSICAL EVIDENCE REQUIRED",
            "warning": WARNING,
        })

    fields = list(rows[0])
    with BINDING.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    source_files = [
        SOURCE / "part-register.csv",
        SOURCE / "geometry-file-register.csv",
        SOURCE / "hold-register.csv",
        ROOT / "bom" / "bom.csv",
        BINDING,
    ]
    status = {
        "identifier": IDENTIFIER,
        "date": "2026-08-09",
        "round": "R148",
        "controlled_architecture": ARCHITECTURE,
        "bom_item_id": "BOM-027",
        "part_count": 5,
        "total_candidate_quantity": 5,
        "geometry_identity_count": 15,
        "inherited_open_hold_count": len(read_csv(SOURCE / "hold-register.csv")),
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in source_files},
        "provider_contacted": False,
        "upload_authorized": False,
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
        f'<article class="card"><div class="part">{html.escape(row["part_id"])}</div>'
        f'<h3>{html.escape(row["part_name"])}</h3><p>Quantity <strong>1</strong></p>'
        f'<p>{html.escape(row["material_candidate"])}</p><p class="state">EXACT CANDIDATE HOLD</p></article>'
        for row in rows
    )
    table_rows = "".join(
        f'<tr><td>{html.escape(row["part_id"])}</td><td><code>{html.escape(row["step_path"])}</code></td>'
        f'<td><code>{html.escape(row["step_sha256"][:16])}…</code></td><td>FALSE</td></tr>'
        for row in rows
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 mechanical BOM binding</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f5fbff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.3rem,5.5vw,4.8rem);line-height:1.03;max-width:18ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.7rem)}}h3{{font-size:1.2rem}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:1rem;margin:2rem 0}}.card{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}.part{{font-size:clamp(1.8rem,3vw,2.6rem);font-weight:900}}.state{{font-weight:900;color:#7a4c00}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:950px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code{{font-size:14px;overflow-wrap:anywhere}}a{{color:#075d98}}</style></head><body><header><div>{IDENTIFIER} · R148 · 2026-08-09</div><h1>Five BOM parts now point to the five controlled P0.7 geometries.</h1><div class="warning">{WARNING}. This corrects configuration identity only; it does not authorize provider contact, upload, quotation, purchase, machining, or use.</div></header><main><p>The live BOM formerly named a superseded P0.5 quantity mix. BOM-027 now binds one each C01, C04, C05, C06 and C07 to the existing 15 hashed STEP, DXF and readable-drawing files.</p><section class="grid">{cards}</section><div class="boundary"><h2>What changed—and what did not</h2><p>The item advances from an unresolved group to an exact-candidate hold. Part identity and candidate quantity are controlled. The fifteen inherited DFM holds remain open, including qualified drawing review, material/MTR, received interface fit, T-slot proof, countersink/fastener stack, stop bumper/load, cables/guard, mass properties, continuous duty, FAI, provider acceptance and physical proof.</p></div><h2>STEP identity preview</h2><div class="table-wrap"><table><thead><tr><th>Part</th><th>Controlled STEP</th><th>SHA-256 prefix</th><th>Upload authorized</th></tr></thead><tbody>{table_rows}</tbody></table></div><div class="boundary"><h2>Next admissible work</h2><p>Qualified mechanical reviewers may inspect and redline the exact files. A separate authorization is required before any provider is contacted or any geometry is uploaded. No fabrication action follows from this binding.</p></div><p><a href="../../../bom/hr-v0-mechanical-custom-part-binding.csv">Download the five-row binding</a> · <a href="../mechanical-dfm-data-p0.1/index.html">Open the detailed DFM/FAI guide</a></p></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: 5 exact parts / 15 inherited geometry identities / 15 open holds")
    print("BOM-027 candidate quantity is five; provider contact, upload, quotation and fabrication remain false")
    print(WARNING)


if __name__ == "__main__":
    main()
