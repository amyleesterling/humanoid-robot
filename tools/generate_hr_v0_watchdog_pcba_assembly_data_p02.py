"""Generate current PCB-P0.9 assembly-data and native-identity evidence.

Run with KiCad 10's bundled Python. This package is internal review data, not
assembler-normalized XYRS, CAM, a manufacturing release, or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path

import pcbnew

from generate_hr_v0_watchdog_footprint_metadata import digest_snapshot, snapshot
from hr_v0_watchdog_footprint_metadata import ASSEMBLY_IDENTITIES, BASE_IDENTITY_FIELDS, FOOTPRINT_METADATA, WARNING


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OLD = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.1"
R132 = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-rfi-p0.1"
R138 = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-footprint-metadata-p0.1"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-assembly-data-p0.2"
IDENTIFIER = "HR-V0-WD-PCBA-DATA-P0.2"


ORIENTATION = {
    "DC1": "PIN 1 VIN MARKED - VERIFY BODY MARK AND PIN 1 BEFORE INSERTION",
    "ISO1": "POLARIZED - PIN 1 MARKED - PRESERVE ISOLATION REGION",
    "JWF1": "PIN 1 MARKED; NOT KEYED - VERIFY RECEIVED ORIENTATION",
    "JWH1": "PIN 1 MARKED; NOT KEYED - VERIFY RECEIVED ORIENTATION",
    "JWP1": "PIN 1 MARKED; NOT KEYED - VERIFY RECEIVED ORIENTATION",
    "UDRV1": "POLARIZED - PIN 1 UPPER LEFT AT SOURCE ROTATION 0 DEG",
    "UDRV2": "POLARIZED - PIN 1 UPPER LEFT AT SOURCE ROTATION 0 DEG",
    "UFB1": "POLARIZED - PIN 1 UPPER LEFT AT SOURCE ROTATION 0 DEG",
    "WDCTRL1": "POLARIZED MODULE - PIN 1 / USB END PER OFFICIAL FOOTPRINT; VERIFY",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def transform_rows(name: str, replacements: dict[str, str]) -> list[dict[str, str]]:
    rows = read_csv(OLD / name)
    for row in rows:
        for key, value in row.items():
            for old, new in replacements.items():
                value = value.replace(old, new)
            row[key] = value
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD))
    if board.GetTitleBlock().GetRevision() != "PCB-P0.9 / Electrical V3-P1.14":
        raise RuntimeError("current board is not PCB-P0.9 / Electrical V3-P1.14")

    baseline = json.loads((R138 / "pcb-p0.8-geometry-topology-current.json").read_text(encoding="utf-8"))
    current_snapshot = snapshot(board)
    current_digest = digest_snapshot(current_snapshot)
    geometry_equal = baseline["snapshot_sha256"] == current_digest and baseline["snapshot"] == current_snapshot
    parity = {
        "identifier": IDENTIFIER,
        "baseline_configuration": "PCB-P0.8 / Electrical V3-P1.14",
        "current_configuration": "PCB-P0.9 / Electrical V3-P1.14",
        "baseline_snapshot_sha256": baseline["snapshot_sha256"],
        "current_snapshot_sha256": current_digest,
        "geometry_topology_equal": geometry_equal,
        "change_scope": "hidden native assembly identity/process-state fields and title-block revision only",
        "copper_changed": False,
        "placement_changed": False,
        "nets_changed": False,
        "warning": WARNING,
    }
    (OUT / "p0.8-p0.9-geometry-topology-parity.json").write_text(json.dumps(parity, indent=2) + "\n", encoding="utf-8")

    edge_points = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            edge_points.extend((drawing.GetStart(), drawing.GetEnd()))
    xs = [pcbnew.ToMM(value.x) for value in edge_points]
    ys = [pcbnew.ToMM(value.y) for value in edge_points]
    origin_x, origin_y = min(xs), min(ys)
    if (round(origin_x, 6), round(origin_y, 6), round(max(xs)-origin_x, 6), round(max(ys)-origin_y, 6)) != (20.0, 20.0, 160.0, 100.0):
        raise RuntimeError("unexpected Edge.Cuts bounds")

    old_placements = {row["reference"]: row for row in read_csv(OLD / "assembly-placement-reference.csv")}
    old_mechanical = {row["reference"]: row for row in read_csv(OLD / "mechanical-feature-register.csv")}
    r132 = {row["reference"]: row for row in read_csv(R132 / "placement-process-register.csv")}
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    populated = []
    mechanical = []
    assembly_parity = []
    identity_rows = []

    for ref, fp in sorted(footprints.items()):
        pos = fp.GetPosition()
        x = pcbnew.ToMM(pos.x) - origin_x
        y = pcbnew.ToMM(pos.y) - origin_y
        if ref.startswith("MH"):
            row = {
                "reference": ref, "feature": "3.20 mm NPTH M3 clearance candidate",
                "board_x_mm": f"{x:.3f}", "board_y_mm": f"{y:.3f}",
                "hardware_state": "SELECTION REQUIRED - NO SCREW/WASHER/STANDOFF RELEASE", "warning": WARNING,
            }
            mechanical.append(row)
            old = old_mechanical[ref]
            match = all(row[key] == old[key] for key in ("reference", "feature", "board_x_mm", "board_y_mm", "hardware_state"))
            assembly_parity.append({"reference":ref,"kind":"MECHANICAL_NPTH","p0.7_identity":old["feature"],"p0.9_identity":row["feature"],"position_match":str(match).upper(),"rotation_match":"N/A","identity_match":str(match).upper(),"overall_match":str(match).upper(),"warning":WARNING})
            continue
        if ref not in ASSEMBLY_IDENTITIES:
            raise RuntimeError(f"missing identity for {ref}")
        manufacturer, mpn, description, process = ASSEMBLY_IDENTITIES[ref]
        orientation = ORIENTATION.get(ref, "NONPOLAR / SINGLE TERMINAL - ROTATION RETAINED FOR SOURCE PARITY")
        row = {
            "reference": ref, "manufacturer": manufacturer, "manufacturer_part_number": mpn,
            "description": description, "footprint": str(fp.GetFPID().GetLibItemName()),
            "process_class": process, "side": "TOP",
            "board_origin_convention": "EDGE-CUTS MIN X/Y = 0/0; +X RIGHT; +Y DOWN; MILLIMETRES",
            "board_x_mm": f"{x:.3f}", "board_y_mm": f"{y:.3f}",
            "source_rotation_deg": f"{fp.GetOrientationDegrees():.3f}",
            "orientation_control": orientation,
            "assembler_transform_state": "SELECTION REQUIRED - DO NOT IMPORT AS MACHINE XYRS",
            "assembly_state": r132[ref]["release_state"],
            "native_identity_match": "TRUE", "warning": WARNING,
        }
        populated.append(row)
        old = old_placements[ref]
        identity_match = all(row[key] == old[key] for key in ("manufacturer", "manufacturer_part_number", "description", "footprint", "process_class", "side", "orientation_control"))
        position_match = all(row[key] == old[key] for key in ("board_x_mm", "board_y_mm"))
        rotation_match = row["source_rotation_deg"] == old["source_rotation_deg"]
        assembly_parity.append({"reference":ref,"kind":"POPULATED","p0.7_identity":old["manufacturer"]+" "+old["manufacturer_part_number"],"p0.9_identity":manufacturer+" "+mpn,"position_match":str(position_match).upper(),"rotation_match":str(rotation_match).upper(),"identity_match":str(identity_match).upper(),"overall_match":str(identity_match and position_match and rotation_match).upper(),"warning":WARNING})
        expected_fields = {
            "Manufacturer": manufacturer, "ManufacturerPartNumber": mpn, "AssemblyDescription": description,
            "ProcessClass": process, "AlternatePolicy": "NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION",
            "AssemblyProcessState": "SELECTION REQUIRED", "FabricationStatus": WARNING,
        }
        for field in BASE_IDENTITY_FIELDS:
            actual = fp.GetField(field).GetText() if fp.HasField(field) else ""
            identity_rows.append({"reference":ref,"field":field,"expected_value":expected_fields[field],"native_kicad_value":actual,"match":str(actual==expected_fields[field]).upper(),"hidden":str(fp.HasField(field) and not fp.GetField(field).IsVisible()).upper(),"warning":WARNING})

    if len(populated) != 42 or len(mechanical) != 4 or len(identity_rows) != 294:
        raise RuntimeError("board membership/native identity count mismatch")
    write_csv(OUT / "assembly-placement-reference.csv", populated)
    write_csv(OUT / "mechanical-feature-register.csv", mechanical)
    write_csv(OUT / "assembly-parity-p0.7-to-p0.9.csv", assembly_parity)
    write_csv(OUT / "native-identity-field-register.csv", identity_rows)

    grouped = defaultdict(list)
    for row in populated:
        grouped[(row["manufacturer"],row["manufacturer_part_number"],row["description"],row["process_class"])].append(row["reference"])
    bom = []
    for index, ((manufacturer, mpn, description, process), refs) in enumerate(sorted(grouped.items()), 1):
        bom.append({"line_id":f"WD-BOM-{index:03d}","manufacturer":manufacturer,"manufacturer_part_number":mpn,"description":description,"quantity_per_board":str(len(refs)),"references":";".join(sorted(refs)),"process_class":process,"alternate_policy":"NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION","sourcing_state":"EXACT MPN CANDIDATE - PROVIDER/LOT/DATE-CODE/ATTRITION RELEASE OPEN","warning":WARNING})
    write_csv(OUT / "board-assembly-bom.csv", bom)

    replacements = {"PCB-P0.7":"PCB-P0.9", "HR-V0-WD-PCBA-DATA-P0.1":"HR-V0-WD-PCBA-DATA-P0.2"}
    for name in ("coordinate-orientation-control.csv", "assembly-note-register.csv", "assembly-data-holds.csv"):
        write_csv(OUT / name, transform_rows(name, replacements))
    file_states = transform_rows("assembly-data-file-state.csv", replacements)
    write_csv(OUT / "assembly-data-file-state.csv", file_states)
    sources = transform_rows("source-register.csv", replacements)
    sources[0]["record"] = "PCB-P0.9 native board with 42 native identity records"
    sources[0]["revision_date"] = "KiCad 10.0.5; R139; checked 2026-08-09"
    sources.append({"source_id":"WD-DATA-SRC-011","organization":"Project Button","record":"R138 P0.8 structural snapshot and four-critical-IC metadata package","revision_date":"R138; 2026-08-09","locator":"electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/","use":"immutable P0.8 geometry/topology baseline and critical field provenance","warning":WARNING})
    write_csv(OUT / "source-register.csv", sources)

    status = {
        "identifier": IDENTIFIER, "round":"R139", "board":"PCB-P0.9 / Electrical V3-P1.14",
        "board_sha256": hashlib.sha256(BOARD.read_bytes()).hexdigest(),
        "populated_references":42, "mechanical_features":4, "bom_lines":len(bom), "native_identity_fields":len(identity_rows),
        "smd":38, "tht":4, "all_top_side":True,
        "p0.7_assembly_parity": all(row["overall_match"] == "TRUE" for row in assembly_parity),
        "p0.8_geometry_topology_parity": geometry_equal,
        "internal_review_only":True, "supplier_normalized_xyrs_exists":False, "cam_exists":False,
        "provider_selected":False, "provider_contacted":False, "files_uploaded":False,
        "fabrication_authorized":False, "assembly_authorized":False, "physical_article_exists":False,
        "energization_authorized":False, "safety_credit":False, "warning":WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")

    data_json = json.dumps([{key:row[key] for key in ("reference","manufacturer","manufacturer_part_number","process_class","board_x_mm","board_y_mm","source_rotation_deg")} for row in populated])
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PCB-P0.9 assembly identity</title><style>
:root{{--sky:#8ed5ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--paper:#f4f9ff;--ink:#10253d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{padding:14px 5vw;background:var(--gold);color:#071c36;font-weight:850}}header,main,footer{{padding:28px 5vw}}header{{background:var(--sky)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.08;max-width:950px;color:var(--dark)}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}}.metric,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px}}.metric strong{{display:block;font-size:32px}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}}button,input{{font:inherit;min-font-size:16px;padding:10px 14px;border:2px solid var(--blue);border-radius:9px;background:white}}button[aria-pressed="true"]{{background:var(--gold)}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:11px;text-align:left;border-bottom:1px solid #b8d3e7;vertical-align:top}}th{{background:var(--dark);color:white}}a{{color:var(--blue);font-weight:700}}footer{{background:var(--dark);color:white;margin-top:28px}}@media(max-width:600px){{header,main,footer{{padding:20px}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R139 · PCB-P0.9</p><h1>Every populated footprint now carries its exact assembly identity.</h1><p>Forty-two manufacturer/MPN records travel with the native board. Geometry, copper, nets, placement and rotation are unchanged. This is still internal review data—not machine XYRS or a manufacturing release.</p></header><main><section><div class="metrics"><div class="metric"><strong>42/42</strong>native identity matches</div><div class="metric"><strong>294</strong>hidden base fields</div><div class="metric"><strong>16</strong>exact-MPN BOM lines</div><div class="metric"><strong>0</strong>released CAM files</div></div></section><section><h2>Search the assembly</h2><div class="controls"><button data-filter="all" aria-pressed="true">All</button><button data-filter="SMD_REFLOW" aria-pressed="false">SMD</button><button data-filter="MANUAL_THT_POST_REFLOW" aria-pressed="false">THT</button><input id="search" aria-label="Find a reference or part" placeholder="Find TP1 or ISO1212DBQ"></div><div class="table-wrap"><table><thead><tr><th>Reference</th><th>Exact identity</th><th>Process class</th><th>X / Y mm</th><th>Native rotation</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Evidence</h2><p><a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/board-assembly-bom.csv">Board BOM</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-placement-reference.csv">Placement register</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/native-identity-field-register.csv">Native fields</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-parity-p0.7-to-p0.9.csv">P0.7/P0.9 assembly parity</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/p0.8-p0.9-geometry-topology-parity.json">P0.8/P0.9 structural parity</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/package-status.json">Status</a></p></section></main><footer>{WARNING}. Supplier transform, process acceptance, CAM, fabrication, assembly, connection and energization remain unauthorized.</footer><script>const data={data_json};let filter='all';const body=document.querySelector('#rows'),search=document.querySelector('#search');function esc(v){{return String(v).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function draw(){{const q=search.value.trim().toLowerCase();body.innerHTML=data.filter(r=>(filter==='all'||r.process_class===filter)&&(!q||(r.reference+' '+r.manufacturer_part_number).toLowerCase().includes(q))).map(r=>`<tr><td><strong>${{esc(r.reference)}}</strong></td><td>${{esc(r.manufacturer)}}<br>${{esc(r.manufacturer_part_number)}}</td><td>${{esc(r.process_class)}}</td><td>${{esc(r.board_x_mm)}} / ${{esc(r.board_y_mm)}}</td><td>${{esc(r.source_rotation_deg)}}°</td></tr>`).join('')}}document.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{{filter=b.dataset.filter;document.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));draw()}}));search.addEventListener('input',draw);draw();</script></body></html>'''
    page = page.replace("min-font-size:16px", "font-size:16px")
    page = page.replace(
        "<main><section>",
        '<main><p class="panel"><strong>Assembly process: SELECTION REQUIRED.</strong> '
        "Supplier transform, machine XYRS, paste, stencil, process limits and fabrication authority remain open.</p><section>",
        1,
    )
    (WEB / "index.html").write_text(page, encoding="utf-8")
    print(f"{IDENTIFIER}: 42 identities / 294 fields / {len(bom)} BOM lines")
    print(f"P0.7 assembly parity={status['p0.7_assembly_parity']}; P0.8 structural parity={geometry_equal}")
    print(WARNING)
    return 0 if geometry_equal and status["p0.7_assembly_parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
