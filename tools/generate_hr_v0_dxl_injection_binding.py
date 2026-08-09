"""Generate the R152 DXL injection allocation/BOM binding evidence."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-injection-binding-p0.1"
IDENTIFIER = "HR-V0-DXL-INJECT-BIND-P0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SYSTEM_SCHEDULE = ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv"
NATIVE_SCHEDULE = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "connector-schedule.csv"
SYSTEM_BOM = ROOT / "electrical" / "kicad" / "project-button-v3" / "bom.csv"
NATIVE_BOARD = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "hr-v0-dxl-star.kicad_pcb"
CAM_STATUS = ROOT / "release" / "hr-v0" / "dxl-star-manufacturing-p0.1" / "package-status.json"
MAP = {
    "CTRL": "JC1", "PWR1": "JP1", "PWR2": "JP2", "PWR3": "JP3",
    "ACT1": "JA1", "ACT2": "JA2", "ACT3": "JA3",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    sources = [SYSTEM_SCHEDULE, NATIVE_SCHEDULE, SYSTEM_BOM, NATIVE_BOARD, CAM_STATUS]
    for path in sources:
        if not path.is_file():
            raise FileNotFoundError(path)
    if OUT.exists():
        resolved = OUT.resolve()
        if resolved.parent != (ROOT / "release" / "hr-v0").resolve() or resolved.name != "dxl-injection-binding-p0.1":
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    OUT.mkdir(parents=True)

    system_rows = [row for row in read_csv(SYSTEM_SCHEDULE) if row["reference"] == "INJ1"]
    native_rows = read_csv(NATIVE_SCHEDULE)
    if len(system_rows) != 18 or len(native_rows) != 18:
        raise RuntimeError("expected 18 system and 18 native injection terminals")
    native_by_key = {(row["reference"], row["terminal"]): row for row in native_rows}
    parity_rows = []
    for row in system_rows:
        prefix, pin = row["terminal"].split(":", 1)
        native_ref = MAP[prefix]
        native = native_by_key[(native_ref, pin)]
        parity = row["net"] == native["net"]
        parity_rows.append({
            "system_reference": "INJ1",
            "system_terminal": row["terminal"],
            "system_pin_name": row["pin_name"],
            "system_net": row["net"],
            "native_reference": native_ref,
            "native_terminal": pin,
            "native_pin_name": native["pin_name"],
            "native_net": native["net"],
            "parity": "PASS" if parity else "FAIL",
            "release_state": "ENCODED ALLOCATION PARITY ONLY - PHYSICAL EVIDENCE OPEN",
            "warning": WARNING,
        })
    if any(row["parity"] != "PASS" for row in parity_rows):
        raise RuntimeError("system/native terminal parity failed")
    write_csv(OUT / "allocation-parity.csv", list(parity_rows[0]), parity_rows)

    system_inj = [row for row in read_csv(SYSTEM_BOM) if row["reference"] == "INJ1"]
    if len(system_inj) != 1 or system_inj[0]["quantity"] != "1" or "DXL-STAR-P0.1" not in system_inj[0]["value"]:
        raise RuntimeError("Electrical V3 does not contain exactly one INJ1 DXL-star board")
    binding = [{
        "legacy_item_id": "BOM-035",
        "legacy_role": "three undefined VDD-isolating injection-module placeholders",
        "disposition": "INTEGRATED IN PARENT - NO SEPARATE PURCHASE",
        "parent_item_id": "BOM-051",
        "parent_identity": "DXL-STAR-P0.1 / HR-V0-DXL-STAR-MFG-P0.1",
        "parent_quantity": "1",
        "system_reference": "INJ1",
        "implemented_branch_count": "3",
        "terminal_count": "18",
        "configuration_result": "one central board implements all three isolated VDD injection branches",
        "residual_boundary": "harness protection connector current thermal waveform no-backfeed grounding physical and qualified-review evidence remain open",
        "warning": WARNING,
    }]
    write_csv(OUT / "bom-allocation-binding.csv", list(binding[0]), binding)

    residuals = [
        ("DXL-BIND-HOLD-001", "BOM-051 fabrication and assembly", "all R151 manufacturing and assembly holds remain open"),
        ("DXL-BIND-HOLD-002", "BOM-052/BOM-053 headers", "received identity, polarity, footprint and application acceptance"),
        ("DXL-BIND-HOLD-003", "BOM-054/BOM-055 signal housing/contact", "wire compatibility, crimp tooling, pull, retention and temperature evidence"),
        ("DXL-BIND-HOLD-004", "BOM-056/BOM-057 power housing/contact", "selected conductor, crimp process, pull, retention and thermal evidence"),
        ("DXL-BIND-HOLD-005", "BOM-061 signal harness", "exact cable construction, lengths, empty U2D2 cavity, strain relief and bend-life evidence"),
        ("DXL-BIND-HOLD-006", "BOM-015 branch protection", "fault, inrush, regeneration, duty, clearing and jurisdiction evidence"),
        ("DXL-BIND-HOLD-007", "BOM-060/BOM-069 conductor and termination", "exact wire/termination order codes, routing, tooling and pull-test acceptance"),
        ("DXL-BIND-HOLD-008", "connector/current conflict", "resolve JST EH 3 A basis versus XM540 4.4 A stall condition"),
        ("DXL-BIND-HOLD-009", "DXL waveform and EMC", "baud/topology/loading/error-rate, routing, shield and common-mode evidence"),
        ("DXL-BIND-HOLD-010", "no-backfeed and power sequencing", "physical open/short/power-sequence tests with JC1.2 omitted"),
        ("DXL-BIND-HOLD-011", "thermal and fault validation", "representative continuous/peak load, fault injection and temperature-rise evidence"),
        ("DXL-BIND-HOLD-012", "qualified review and work authority", "independent electrical/manufacturing disposition plus separate written work authorization"),
    ]
    hold_rows = [{"hold_id": i, "subject": s, "status": "OPEN", "evidence_needed": e, "warning": WARNING} for i, s, e in residuals]
    write_csv(OUT / "residual-holds.csv", list(hold_rows[0]), hold_rows)

    source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in sources}
    cam_status = json.loads(CAM_STATUS.read_text(encoding="utf-8"))
    status = {
        "identifier": IDENTIFIER,
        "round": "R152",
        "date": "2026-08-09",
        "legacy_item": "BOM-035",
        "parent_item": "BOM-051",
        "parent_board": "DXL-STAR-P0.1",
        "parent_manufacturing_review": "HR-V0-DXL-STAR-MFG-P0.1",
        "system_reference": "INJ1",
        "parent_quantity": 1,
        "implemented_branches": 3,
        "terminal_parity_rows": 18,
        "terminal_parity_failures": 0,
        "residual_holds": 12,
        "source_hashes": source_hashes,
        "parent_cam_review_only": cam_status.get("cam_review_only") is True,
        "separate_bom035_purchase_required": False,
        "supplier_selected": False,
        "supplier_contacted": False,
        "files_uploaded": False,
        "quotation_requested": False,
        "purchase_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "physical_article_exists": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    write_text(OUT / "package-status.json", json.dumps(status, indent=2) + "\n")

    readme = f"""# {IDENTIFIER}\n\n> **{WARNING}**\n\nR152 removes a duplicate configuration allocation: legacy `BOM-035` described three separate injection modules, but current Electrical V3 and native DXL-STAR-P0.1 contain one central `INJ1` board implementing all three isolated VDD branches. `BOM-035` is therefore integrated in parent `BOM-051` and has no separate purchase.\n\nThis package proves allocation and encoded terminal parity only. It does not release BOM-051, connectors, harnesses, protection, conductors, fabrication, assembly, connection, motion or energization. Twelve residual boundaries remain open.\n"""
    write_text(OUT / "README.md", readme)

    hold_html = "".join(f"<li><strong>{i}</strong> {html.escape(s)}<br><span>{html.escape(e)}</span></li>" for i, s, e in residuals)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.3rem,5.5vw,4.8rem);line-height:1.03;max-width:18ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.7rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:940px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code{{font-size:14px}}li{{margin:.8rem 0}}li span{{font-size:14px}}</style></head><body><header><div>{IDENTIFIER} · R152 · 2026-08-09</div><h1>One board replaces three placeholders.</h1><div class="warning">{WARNING}. This is a configuration correction, not a hardware release.</div></header><main><p>Electrical V3 contains one <code>INJ1</code>. Native DXL-STAR-P0.1 implements its three isolated actuator VDD branches. Legacy BOM-035 is integrated in BOM-051; no separate three-module purchase remains.</p><section class="grid"><article><b>1</b>central parent board</article><article><b>3</b>isolated VDD branches</article><article><b>18</b>system/native terminal parity rows</article><article><b>0</b>work authorizations</article></section><div class="boundary"><h2>What changed—and what did not</h2><p>The duplicate quantity is removed. BOM-051 remains an exact candidate hold, and the harness, connectors, contacts, protection, conductors, current conflict, waveform, no-backfeed, grounding, thermal and physical evidence remain open.</p></div><h2>Allocation binding</h2><div class="table-wrap"><table><thead><tr><th>Legacy item</th><th>Disposition</th><th>Parent</th><th>Implementation</th></tr></thead><tbody><tr><td>BOM-035</td><td>INTEGRATED — NO SEPARATE PURCHASE</td><td>BOM-051 / DXL-STAR-P0.1</td><td>INJ1: one board, three branches, eighteen terminals</td></tr></tbody></table></div><div class="boundary"><h2>Twelve residual holds remain open</h2><ol>{hold_html}</ol></div><p><a href="bom-allocation-binding.csv">BOM binding</a> · <a href="allocation-parity.csv">terminal allocation parity</a> · <a href="residual-holds.csv">residual holds</a></p></main></body></html>'''
    write_text(OUT / "index.html", page)

    manifest_rows = [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")]
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256"], manifest_rows)
    print(f"{IDENTIFIER}: BOM-035 integrated in BOM-051; 1 board / 3 branches / 18 terminal parity rows / 12 holds OPEN")
    print(WARNING)


if __name__ == "__main__":
    main()
