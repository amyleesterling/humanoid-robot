#!/usr/bin/env python3
"""Generate the R245 integrated-configuration successor mechanical binding."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.3.csv"
PRIOR = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv"
OUT = ROOT / "release/hr-v0/mechanical-bom-binding-p0.3"
IDENT = "HR-V0-MECH-BOM-BIND-P0.3"
ARCH = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing headerless CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def put(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def main() -> None:
    rows = read(SOURCE)
    if len(rows) != 5 or {r["part_id"] for r in rows} != {"MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"}:
        raise ValueError("P0.3 binding must cover the five exact custom parts")
    for row in rows:
        if row["architecture_id"] != ARCH or row["quantity_candidate"] != "1":
            raise ValueError(f"stale architecture or quantity at {row['part_id']}")
        for field in ("step_path", "dxf_path", "drawing_path"):
            path = ROOT / row[field]
            hash_field = field.replace("_path", "_sha256")
            if not path.is_file() or digest(path) != row[hash_field]:
                raise ValueError(f"source hash mismatch at {row['part_id']} {field}")
        if row["quotation_authorized"] != "FALSE" or row["fabrication_authorized"] != "FALSE" or row["warning"] != WARNING:
            raise ValueError(f"work boundary changed at {row['part_id']}")

    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "mechanical-custom-part-binding-p0.3.csv", rows)
    write(OUT / "supersession-map.csv", [{
        "prior_identifier": "HR-V0-MECH-BOM-BIND-P0.2",
        "successor_identifier": IDENT,
        "change": f"corrects all five architecture_id values to {ARCH}; geometry and fifteen STEP/DXF/drawing hashes are unchanged",
        "prior_artifacts_historical": "TRUE",
        "fabrication_authorized": "FALSE",
        "warning": WARNING,
    }])
    holds = [
        ("MB3-H01", "Issue successor shop drawings that name the integrated P0.8 configuration and remove stale P0.7/nonselected active wording"),
        ("MB3-H02", "Qualified drafting/metrology disposition of datum scheme, GD&T standard/revision, uncertainty and acceptance rules"),
        ("MB3-H03", "Complete title blocks, general tolerances, surface finish, marking, cleaning, preservation and packaging requirements"),
        ("MB3-H04", "Exact material specification edition, product form, certificate and no-substitution purchase requirement"),
        ("MB3-H05", "Active RFQ payload manifest, line items, supplier deviation response and deterministic package hash"),
        ("MB3-H06", "Part-specific unpowered assembly orientation and work instruction with held torque/locking/tool fields"),
        ("MB3-H07", "Provider DFM acceptance, MTR, thirty-operation FAI and raw measurement return"),
        ("MB3-H08", "Received identity, fit, mass properties, dry assembly, structural and stop proof"),
        ("MB3-H09", "Qualified mechanical review and signed work authorization"),
    ]
    write(OUT / "open-holds.csv", [{"hold_id": hid, "hold": hold, "state": "OPEN", "evidence": "SELECTION REQUIRED / NOT EXECUTED", "warning": WARNING} for hid, hold in holds])
    source_register = [
        {"source_path": SOURCE.relative_to(ROOT).as_posix(), "sha256": digest(SOURCE), "role": "current corrected binding", "warning": WARNING},
        {"source_path": PRIOR.relative_to(ROOT).as_posix(), "sha256": digest(PRIOR), "role": "historical predecessor", "warning": WARNING},
        {"source_path": "release/hr-v0/arm-architecture-p0.8-dwg-integrated/source-hash-register.csv", "sha256": digest(ROOT / "release/hr-v0/arm-architecture-p0.8-dwg-integrated/source-hash-register.csv"), "role": "integrated assembly evidence", "warning": WARNING},
    ]
    write(OUT / "source-hash-register.csv", source_register)
    status = {
        "identifier": IDENT,
        "round": "R245",
        "date": "2026-08-11",
        "architecture_id": ARCH,
        "part_count": 5,
        "quantity_each": 1,
        "controlled_identity_count": 15,
        "geometry_changed_from_p0_2": False,
        "stale_architecture_identifier_corrected": True,
        "open_holds": len(holds),
        "shop_drawings_released": False,
        "provider_contacted": False,
        "quotation_authorized": False,
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
    put(OUT / "package-status.json", json.dumps(status, indent=2) + "\n")
    put(OUT / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR245 corrects the five-part manufacturing binding to the current integrated P0.8 arm identity without changing geometry or releasing the stale P0.1 shop drawings. Nine fabrication-definition and physical holds remain.\n")
    part_rows = "".join(f"<tr><td>{html.escape(r['part_id'])}</td><td>{html.escape(r['part_name'])}</td><td>{r['quantity_candidate']}</td><td><code>{html.escape(r['step_sha256'][:12])}...</code></td><td>{html.escape(r['release_state'])}</td></tr>" for r in rows)
    hold_rows = "".join(f"<li><b>{html.escape(hid)}</b> {html.escape(hold)}</li>" for hid, hold in holds)
    put(OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENT}</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:32px clamp(16px,4vw,48px)}}h1{{font-size:clamp(32px,5vw,64px);line-height:1.05}}.warning{{padding:16px;border:3px solid #9b6d00;background:#fff3c4;font-weight:800;border-radius:12px}}.card{{background:#fff;border:2px solid var(--blue);border-radius:12px;padding:20px;margin:24px 0}}.table{{overflow:auto}}table{{border-collapse:collapse;min-width:980px;width:100%}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}li{{margin:.75rem 0}}</style></head><body><header><b>R245 · {IDENT}</b><h1>The five custom parts now point at the same robot.</h1><div class="warning">{WARNING}</div></header><main><div class="card"><b>Configuration defect corrected.</b><p>P0.2 named the pre-integration drawing candidate. P0.3 names <code>{ARCH}</code> for all five exact, one-each parts. The fifteen source hashes are unchanged.</p><p>This is configuration repair, not a machining release. The inherited P0.1 drawings still need a controlled shop-document successor.</p></div><div class="table"><table><thead><tr><th>Part</th><th>Name</th><th>Qty</th><th>STEP hash</th><th>Boundary</th></tr></thead><tbody>{part_rows}</tbody></table></div><h2>What remains before a machinist packet exists</h2><ol>{hold_rows}</ol></main></body></html>''')
    files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    write(OUT / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENT}: 5 parts / 15 unchanged identities / {len(holds)} open holds")


if __name__ == "__main__":
    main()
