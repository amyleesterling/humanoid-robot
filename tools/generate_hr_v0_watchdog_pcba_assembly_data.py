"""Generate the R133 PCB-P0.7 assembly-data review package.

Run with KiCad 10's bundled Python. Outputs are internal review artifacts,
not supplier-normalized placement data, CAM, or manufacturing authorization.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
R132 = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-rfi-p0.1"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-assembly-data-p0.1"
IDENTIFIER = "HR-V0-WD-PCBA-DATA-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

PARTS = {
    "CDEC1": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805"),
    "CDRV1": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805"),
    "CDRV2": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805"),
    "CFI1": ("TDK", "CGA3E2X7R1H103K080AA", "10 nF, 50 V, X7R, 0603"),
    "CFI2": ("TDK", "CGA3E2X7R1H103K080AA", "10 nF, 50 V, X7R, 0603"),
    "DC1": ("TRACO POWER", "TSR 1-2450", "24 V to 5 V, 1 A, non-isolated"),
    "ISO1": ("Vishay", "VO618A-4X017T", "phototransistor optocoupler, option 7"),
    "JWF1": ("Phoenix Contact", "1751248", "MKDS 1/2-3,5, 2 position"),
    "JWH1": ("Phoenix Contact", "1751248", "MKDS 1/2-3,5, 2 position"),
    "JWP1": ("Phoenix Contact", "1751264", "MKDS 1/4-3,5, 4 position"),
    "RHB1": ("Panasonic Industry", "ERJ6ENF9100V", "910 ohm, 1%, 0805, 0.125 W"),
    "RHP1": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W"),
    "RPD1": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W"),
    "RPD2": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W"),
    "RSN1": ("Panasonic Industry", "ERJ6ENF5620V", "562 ohm, 1%, 0805"),
    "RSN2": ("Panasonic Industry", "ERJ6ENF5620V", "562 ohm, 1%, 0805"),
    "RSO1": ("Panasonic Industry", "ERJ6ENF1001V", "1.00 kohm, 1%, 0805"),
    "RSO2": ("Panasonic Industry", "ERJ6ENF1001V", "1.00 kohm, 1%, 0805"),
    "RTH1": ("Vishay", "MMA02040C1001FB300", "1.00 kohm, 1%, 0.4 W, MELF"),
    "RTH2": ("Vishay", "MMA02040C1001FB300", "1.00 kohm, 1%, 0.4 W, MELF"),
    "RW1": ("Vishay", "CRCW12102K70FKEA", "2.70 kohm, 1%, 0.5 W, 1210"),
    "RW2": ("Vishay", "CRCW12102K70FKEA", "2.70 kohm, 1%, 0.5 W, 1210"),
    **{f"TP{i}": ("Harwin", "S1751-46R", "SMT test point") for i in range(1, 17)},
    "UDRV1": ("Texas Instruments", "TPL7407LPWR", "seven-channel low-side driver, PW0016A"),
    "UDRV2": ("Texas Instruments", "TPL7407LPWR", "seven-channel low-side driver, PW0016A"),
    "UFB1": ("Texas Instruments", "ISO1212DBQ", "dual isolated 24 V input receiver, DBQ0016A"),
    "WDCTRL1": ("Raspberry Pi", "SC0915", "Raspberry Pi Pico 1 / RP2040 module"),
}

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


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD))
    edge_points = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            edge_points.extend((drawing.GetStart(), drawing.GetEnd()))
    if not edge_points:
        raise RuntimeError("board has no Edge.Cuts geometry")
    xs = [pcbnew.ToMM(point.x) for point in edge_points]
    ys = [pcbnew.ToMM(point.y) for point in edge_points]
    origin_x, origin_y = min(xs), min(ys)
    width, height = max(xs) - origin_x, max(ys) - origin_y
    if (round(origin_x, 6), round(origin_y, 6), round(width, 6), round(height, 6)) != (20.0, 20.0, 160.0, 100.0):
        raise RuntimeError(f"unexpected board edge box: {origin_x}, {origin_y}, {width}, {height}")

    r132_rows = {}
    with (R132 / "placement-process-register.csv").open(newline="", encoding="utf-8") as handle:
        r132_rows = {row["reference"]: row for row in csv.DictReader(handle)}

    placements: list[dict] = []
    mechanical: list[dict] = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        ref = fp.GetReference()
        pos = fp.GetPosition()
        x = pcbnew.ToMM(pos.x) - origin_x
        y = pcbnew.ToMM(pos.y) - origin_y
        if ref.startswith("MH"):
            mechanical.append({
                "reference": ref,
                "feature": "3.20 mm NPTH M3 clearance candidate",
                "board_x_mm": f"{x:.3f}",
                "board_y_mm": f"{y:.3f}",
                "hardware_state": "SELECTION REQUIRED - NO SCREW/WASHER/STANDOFF RELEASE",
                "warning": WARNING,
            })
            continue
        if ref not in PARTS:
            raise RuntimeError(f"missing exact part mapping for {ref}")
        maker, mpn, description = PARTS[ref]
        process = r132_rows[ref]["process_class"]
        orientation = ORIENTATION.get(ref, "NONPOLAR / SINGLE TERMINAL - ROTATION RETAINED FOR SOURCE PARITY")
        placements.append({
            "reference": ref,
            "manufacturer": maker,
            "manufacturer_part_number": mpn,
            "description": description,
            "footprint": fp.GetFPID().GetLibItemName(),
            "process_class": process,
            "side": "TOP",
            "board_origin_convention": "EDGE-CUTS MIN X/Y = 0/0; +X RIGHT; +Y DOWN; MILLIMETRES",
            "board_x_mm": f"{x:.3f}",
            "board_y_mm": f"{y:.3f}",
            "source_rotation_deg": f"{fp.GetOrientationDegrees():.3f}",
            "orientation_control": orientation,
            "assembler_transform_state": "SELECTION REQUIRED - DO NOT IMPORT AS MACHINE XYRS",
            "assembly_state": r132_rows[ref]["release_state"],
            "warning": WARNING,
        })
    if len(placements) != 42 or len(mechanical) != 4:
        raise RuntimeError("expected 42 populated references and four NPTH features")
    write_csv(OUT / "assembly-placement-reference.csv", placements)
    write_csv(OUT / "mechanical-feature-register.csv", mechanical)

    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for row in placements:
        key = (row["manufacturer"], row["manufacturer_part_number"], row["description"], row["process_class"])
        grouped[key].append(row["reference"])
    bom = []
    for index, ((maker, mpn, description, process), refs) in enumerate(sorted(grouped.items()), 1):
        bom.append({
            "line_id": f"WD-BOM-{index:03d}",
            "manufacturer": maker,
            "manufacturer_part_number": mpn,
            "description": description,
            "quantity_per_board": str(len(refs)),
            "references": ";".join(sorted(refs)),
            "process_class": process,
            "alternate_policy": "NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION",
            "sourcing_state": "EXACT MPN CANDIDATE - PROVIDER/LOT/DATE-CODE/ATTRITION RELEASE OPEN",
            "warning": WARNING,
        })
    write_csv(OUT / "board-assembly-bom.csv", bom)

    conventions = [
        {"control_id":"WD-DATA-001","subject":"board outline","controlled_definition":"160.000 x 100.000 mm Edge.Cuts bounding box; source absolute minimum X/Y 20.000/20.000 mm","use":"derive review coordinates only","state":"CONTROLLED SOURCE FACT","warning":WARNING},
        {"control_id":"WD-DATA-002","subject":"review origin","controlled_definition":"board-relative origin at minimum Edge.Cuts X/Y; +X right; +Y down; millimetres","use":"human review and assembler discussion","state":"INTERNAL REVIEW CONVENTION","warning":WARNING},
        {"control_id":"WD-DATA-003","subject":"rotation","controlled_definition":"native KiCad footprint orientation degrees copied without supplier transform","use":"source-parity review only","state":"NOT ASSEMBLER-NORMALIZED","warning":WARNING},
        {"control_id":"WD-DATA-004","subject":"side","controlled_definition":"all 42 populated references are on top side","use":"assembly planning","state":"CONTROLLED SOURCE FACT","warning":WARNING},
        {"control_id":"WD-DATA-005","subject":"machine import","controlled_definition":"supplier must define centroid, zero-angle, axis, side and feeder conventions and return a transformed file for written disposition","use":"prevents direct machine import","state":"PROHIBITED UNTIL SUPPLIER CONVENTION ACCEPTED","warning":WARNING},
    ]
    write_csv(OUT / "coordinate-orientation-control.csv", conventions)

    notes_data = [
        ("WD-NOTE-001","scope","Populate 42 references on the top side; four MH references are unpopulated NPTH mechanical features."),
        ("WD-NOTE-002","substitution","Use exact manufacturer part numbers only; no alternate or process substitution without written disposition."),
        ("WD-NOTE-003","SMT","Thirty-eight SMD placements are proposed for reflow; supplier acceptance of every land, mask, paste, stencil and profile remains required."),
        ("WD-NOTE-004","THT","Install DC1, JWP1, JWF1 and JWH1 after reflow using an accepted THT method; seating, trim, flux, cleaning and underside envelope remain open."),
        ("WD-NOTE-005","isolation","Preserve ISO1 copper separation and keep the isolation region free of contamination, unauthorized copper, mask changes and rework residue."),
        ("WD-NOTE-006","Pico","WDCTRL1 is an SC0915 module; official footprint, USB-end orientation, presentation, reflow/fixture and inspection require assembler acceptance."),
        ("WD-NOTE-007","test points","TP1-TP16 use rectangular 3.45 x 1.85 mm Harwin lands; placement, reel convention, access and inspection remain review items."),
        ("WD-NOTE-008","inspection","Verify polarized references and every not-keyed terminal block against received markings before soldering."),
        ("WD-NOTE-009","first article","Hold one first article for documented board, component, orientation, solder, cleanliness, geometry and unpowered electrical review."),
        ("WD-NOTE-010","release","These files are internal review data. They are not machine-ready XYRS, CAM, a purchase order, or fabrication/assembly authorization."),
    ]
    notes = [{"note_id":i,"topic":t,"note":n,"acceptance_state":"OPEN - QUALIFIED/SUPPLIER DISPOSITION REQUIRED" if i != "WD-NOTE-010" else "MANDATORY RELEASE BOUNDARY","warning":WARNING} for i,t,n in notes_data]
    write_csv(OUT / "assembly-note-register.csv", notes)

    file_states_data = [
        ("WD-FILE-001","native KiCad PCB","current PCB-P0.7 source","CURRENT SOURCE - INTERNAL"),
        ("WD-FILE-002","board assembly BOM","board-assembly-bom.csv","INTERNAL REVIEW CANDIDATE - NOT RELEASED"),
        ("WD-FILE-003","placement reference","assembly-placement-reference.csv","INTERNAL REVIEW CANDIDATE - NOT MACHINE XYRS"),
        ("WD-FILE-004","assembly reference map","assembly-top-reference.svg","INTERNAL REVIEW CANDIDATE - NOT RELEASED"),
        ("WD-FILE-005","assembly notes","assembly-note-register.csv","INTERNAL REVIEW CANDIDATE - NOT RELEASED"),
        ("WD-FILE-006","Gerber/drill","SELECTION REQUIRED","DOES NOT EXIST FOR PCB-P0.7"),
        ("WD-FILE-007","IPC-356/netlist","SELECTION REQUIRED","NOT RELEASED"),
        ("WD-FILE-008","assembler-normalized XYRS","supplier convention and written transform disposition","DOES NOT EXIST"),
        ("WD-FILE-009","fabrication drawing/stackup","material/stack/finish/mask/legend/panel choices","DOES NOT EXIST"),
        ("WD-FILE-010","supplier packet manifest","hash-bound accepted CAM/BOM/XYRS/drawings/traveler","DOES NOT EXIST"),
    ]
    file_states = [{"file_id":i,"artifact":a,"definition":d,"state":s,"warning":WARNING} for i,a,d,s in file_states_data]
    write_csv(OUT / "assembly-data-file-state.csv", file_states)

    holds_data = [
        ("WD-DATA-HOLD-001","supplier coordinate convention","exact origin, axes, rotation zero/direction, side mirroring and centroid rule"),
        ("WD-DATA-HOLD-002","reference-level DFM","written acceptance/redline for all 42 populated references and four holes"),
        ("WD-DATA-HOLD-003","exact sourcing route","provider, authorized distributor/consignment, lot/date code, attrition and no-alternate controls"),
        ("WD-DATA-HOLD-004","SMT process","paste/alloy/flux, stencil/apertures, placement, profile, cleaning and inspection"),
        ("WD-DATA-HOLD-005","THT process","method, fixture, seating, solder/flux, trim, cleaning and underside envelope"),
        ("WD-DATA-HOLD-006","ISO1 insulation/cleanliness","working environment, mask/process, contamination criterion and qualified disposition"),
        ("WD-DATA-HOLD-007","Pico presentation/inspection","SC0915 packaging, moisture/process, fixture, reflow and joint inspection"),
        ("WD-DATA-HOLD-008","fabrication definition","material, stack, copper, finish, mask, legend, panel, tolerances and electrical test"),
        ("WD-DATA-HOLD-009","first article","received article plus inspection, traceability, cleanliness and unpowered test evidence"),
        ("WD-DATA-HOLD-010","independent qualified review","PCB/assembly/electrical/insulation/mechanical dispositions"),
        ("WD-DATA-HOLD-011","supplier packet","accepted immutable CAM/BOM/XYRS/drawings/traveler and hashes"),
        ("WD-DATA-HOLD-012","work authorization","separate written upload/quotation/fabrication/assembly authority"),
    ]
    holds = [{"hold_id":i,"subject":s,"status":"OPEN","evidence_needed":e,"warning":WARNING} for i,s,e in holds_data]
    write_csv(OUT / "assembly-data-holds.csv", holds)

    sources_data = [
        ("WD-DATA-SRC-001","Project Button","PCB-P0.7 native board","KiCad 10.0.5; checked 2026-08-09",str(BOARD.relative_to(ROOT)).replace("\\","/"),"geometry, membership, placement and rotation"),
        ("WD-DATA-SRC-002","Project Button","R132 placement/process register","R132; 2026-08-09",str((R132 / "placement-process-register.csv").relative_to(ROOT)).replace("\\","/"),"process and hold state"),
        ("WD-DATA-SRC-003","Project Button","R89 land-pattern audit","R89; rechecked 2026-08-09","release/hr-v0/watchdog-pcb-land-pattern-audit-p0.1/land-pattern-audit.csv","part/footprint/orientation basis"),
        ("WD-DATA-SRC-004","Texas Instruments","TPL7407L / ISO1212 datasheets and package drawings","SLRS066D 2016-03; SLLSEY7G 2025-02; rechecked 2026-08-09","https://www.ti.com/lit/ds/symlink/tpl7407l.pdf ; https://www.ti.com/lit/ds/symlink/iso1212.pdf","UDRV1/2 and UFB1 identity/orientation"),
        ("WD-DATA-SRC-005","Vishay","VO618A / MMA0204 / CRCW records","2025-01-22; 2022-07-12; 2026-04-14; rechecked 2026-08-09","https://www.vishay.com/docs/83432/vo618a.pdf ; https://www.vishay.com/doc/?28950= ; https://www.vishay.com/docs/20035/dcrcwe3.pdf","ISO1 and resistor identities"),
        ("WD-DATA-SRC-006","Murata / TDK / Panasonic","current passive records","2025-01-09; 2026-06; 2025-12-24; rechecked 2026-08-09","electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/source-register.csv","capacitor and resistor identities"),
        ("WD-DATA-SRC-007","Harwin","S1751-46R technical drawing","DRG 02202 issue 10; 2023-02-15; rechecked 2026-08-09","https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf","TP1-TP16 identity and land"),
        ("WD-DATA-SRC-008","Raspberry Pi","Pico 1 product/datasheet","datasheet release 2026-07-03; rechecked 2026-08-09","https://www.raspberrypi.com/products/raspberry-pi-pico/","SC0915 module identity"),
        ("WD-DATA-SRC-009","TRACO POWER","TSR 1 series datasheet","2024-02-07; rechecked 2026-08-09","https://www.tracopower.com/tsr1-datasheet","TSR 1-2450 identity/orientation"),
        ("WD-DATA-SRC-010","Phoenix Contact","MKDS 1/2 and 1/4 product records","accessed 2026-08-08; rechecked 2026-08-09","https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248 ; https://www.phoenixcontact.com/gb/products/1751264/pdf","terminal-block identities/orientation"),
    ]
    sources = [{"source_id":i,"organization":o,"record":r,"revision_date":d,"locator":l,"use":u,"warning":WARNING} for i,o,r,d,l,u in sources_data]
    write_csv(OUT / "source-register.csv", sources)

    scale = 6.0
    marks = []
    for row in placements:
        x = 40 + float(row["board_x_mm"]) * scale
        y = 50 + float(row["board_y_mm"]) * scale
        process_class = "smd" if row["process_class"] == "SMD_REFLOW" else "tht"
        marks.append(f'<g class="part {process_class}" data-ref="{row["reference"]}"><circle cx="{x:.1f}" cy="{y:.1f}" r="8"/><text x="{x + 10:.1f}" y="{y + 5:.1f}">{html.escape(row["reference"])}</text></g>')
    for row in mechanical:
        x = 40 + float(row["board_x_mm"]) * scale
        y = 50 + float(row["board_y_mm"]) * scale
        marks.append(f'<g class="part hole" data-ref="{row["reference"]}"><circle cx="{x:.1f}" cy="{y:.1f}" r="8"/><text x="{x + 10:.1f}" y="{y + 5:.1f}">{row["reference"]}</text></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 700" role="img" aria-labelledby="title desc"><title id="title">PCB-P0.7 top assembly reference map</title><desc id="desc">Board-relative map of 42 populated references and four mounting holes. Review only.</desc><style>text{{font:14px system-ui,sans-serif;fill:#10253d}}.outline{{fill:#f8fcff;stroke:#07579f;stroke-width:5}}.part circle{{fill:#f4bd28;stroke:#082f5b;stroke-width:2}}.tht circle{{fill:#8ed5ff}}.hole circle{{fill:#fff;stroke:#a33;stroke-width:4}}</style><rect class="outline" x="40" y="50" width="960" height="600" rx="12"/>{''.join(marks)}<text x="40" y="685">Origin: top-left Edge.Cuts corner; +X right; +Y down. Not machine-ready XYRS. {WARNING}</text></svg>'''
    (OUT / "assembly-top-reference.svg").write_text(svg, encoding="utf-8")

    status = {
        "identifier": IDENTIFIER,
        "round": "R133",
        "board": "PCB-P0.7",
        "board_sha256": hashlib.sha256(BOARD.read_bytes()).hexdigest(),
        "populated_references": len(placements),
        "mechanical_features": len(mechanical),
        "bom_lines": len(bom),
        "smd": sum(row["process_class"] == "SMD_REFLOW" for row in placements),
        "tht": sum(row["process_class"] == "MANUAL_THT_POST_REFLOW" for row in placements),
        "all_top_side": all(row["side"] == "TOP" for row in placements),
        "internal_review_only": True,
        "supplier_normalized_xyrs_exists": False,
        "cam_exists": False,
        "provider_selected": False,
        "provider_contacted": False,
        "files_uploaded": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "physical_article_exists": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    data_json = json.dumps([{k: row[k] for k in ("reference","manufacturer","manufacturer_part_number","process_class","board_x_mm","board_y_mm","source_rotation_deg","orientation_control")} for row in placements])
    html_doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PCB-P0.7 assembly data</title><style>
:root{{--sky:#dff3ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--ink:#10253d;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;font:17px/1.5 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header,main,footer{{max-width:1200px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:8px solid var(--gold)}}.warning{{background:var(--dark);color:#fff;padding:14px 18px;font-weight:800}}.meta,footer{{font-size:14px}}h1{{font-size:clamp(34px,6vw,66px);line-height:1.06;color:var(--dark)}}h2{{font-size:clamp(26px,4vw,40px);color:var(--blue)}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}}.metric,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px;box-shadow:6px 6px 0 var(--gold)}}.metric strong{{display:block;font-size:32px;color:var(--dark)}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}}button,input{{font:inherit;font-size:16px;padding:10px 14px;border:2px solid var(--blue);border-radius:10px;background:#fff;color:var(--dark)}}button[aria-pressed="true"]{{background:var(--gold)}}.map{{overflow:auto}}.map svg{{display:block;min-width:760px;width:100%;height:auto}}table{{border-collapse:collapse;width:100%;min-width:860px}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #a8c8df;vertical-align:top}}th{{background:var(--dark);color:#fff}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px}}a{{color:var(--blue);font-weight:700}}footer{{border-top:2px solid var(--blue);margin-top:28px}}@media(max-width:600px){{body{{font-size:16px}}header,main,footer{{padding:20px}}.meta,footer{{font-size:14px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p class="meta">{IDENTIFIER} · R133 · PCB-P0.7</p><h1>Assembly data you can inspect—not manufacture from.</h1><p>The exact BOM, board-relative coordinates and orientation controls are now reviewable. A supplier must still define and return its machine convention before any XYRS import or manufacturing release.</p></header><main><section><h2>Controlled scope</h2><div class="metrics"><div class="metric"><strong>{len(placements)}</strong>populated references</div><div class="metric"><strong>{len(bom)}</strong>exact-MPN BOM lines</div><div class="metric"><strong>38 / 4</strong>SMD / THT</div><div class="metric"><strong>0</strong>released CAM files</div></div></section><section><h2>Explore the top assembly</h2><div class="controls"><button data-filter="all" aria-pressed="true">All</button><button data-filter="SMD_REFLOW" aria-pressed="false">SMD</button><button data-filter="MANUAL_THT_POST_REFLOW" aria-pressed="false">THT</button><input id="search" aria-label="Find a reference" placeholder="Find TP1, ISO1, UFB1…"></div><div class="panel map">{svg}</div></section><section><h2>Reference placement register</h2><div class="table-wrap"><table><thead><tr><th>Reference</th><th>Exact part</th><th>Process</th><th>X / Y mm</th><th>Rotation</th><th>Orientation control</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Controlled files</h2><p><a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/board-assembly-bom.csv">Board assembly BOM</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-placement-reference.csv">Placement reference</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/coordinate-orientation-control.csv">Coordinate controls</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-note-register.csv">Assembly notes</a> · <a href="../../../electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-data-holds.csv">Open holds</a></p></section></main><footer>{WARNING}. Do not upload, quote, fabricate, assemble, connect or energize from these internal review files.</footer><script>
const data={data_json};let filter='all';const tbody=document.querySelector('#rows');const search=document.querySelector('#search');function esc(v){{return String(v).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function draw(){{const q=search.value.trim().toLowerCase();const visible=data.filter(r=>(filter==='all'||r.process_class===filter)&&(!q||r.reference.toLowerCase().includes(q)||r.manufacturer_part_number.toLowerCase().includes(q)));tbody.innerHTML=visible.map(r=>`<tr><td><strong>${{esc(r.reference)}}</strong></td><td>${{esc(r.manufacturer)}}<br>${{esc(r.manufacturer_part_number)}}</td><td>${{esc(r.process_class)}}</td><td>${{esc(r.board_x_mm)}} / ${{esc(r.board_y_mm)}}</td><td>${{esc(r.source_rotation_deg)}}°</td><td>${{esc(r.orientation_control)}}</td></tr>`).join('');document.querySelectorAll('.part').forEach(g=>{{const ref=g.dataset.ref;const row=data.find(r=>r.reference===ref);g.style.display=row&&visible.includes(row)?'':'none'}})}}document.querySelectorAll('button[data-filter]').forEach(b=>b.addEventListener('click',()=>{{filter=b.dataset.filter;document.querySelectorAll('button[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));draw()}}));search.addEventListener('input',draw);draw();
</script></body></html>'''
    (WEB / "index.html").write_text(html_doc, encoding="utf-8")

    print(f"Generated {IDENTIFIER}: {len(placements)} populated refs, {len(bom)} BOM lines, {len(mechanical)} NPTH features")
    print("Internal review data only; no supplier-normalized XYRS, CAM, upload, fabrication, assembly or energization authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
