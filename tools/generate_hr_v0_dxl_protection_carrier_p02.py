#!/usr/bin/env python3
"""Generate the corrected P0.2 TPS25946 carrier candidate.

This wraps the P0.1 circuit generator while replacing the defective RPW0010A
land pattern with the geometry published in TI drawing 4225183/A. R156/P0.1
remains immutable historical evidence. P0.2 is still an evaluation candidate,
not a fabrication or energization release.
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

import pcbnew

import generate_hr_v0_dxl_protection_carrier_p01 as base


ROOT = Path(__file__).resolve().parents[1]
base.OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.2"
base.RELEASE = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.2"
base.PROJECT = "hr-v0-dxl-protection-carrier-p0.2"
base.IDENTIFIER = "HR-V0-DXL-PROT-CARRIER-P0.2"
base.REVISION = "DXL-PROT-CARRIER-P0.2"
base.SILK_REVISION = "P0.2"
base.DATE = "2026-08-09"

OUT = base.OUT
RELEASE = base.RELEASE
PROJECT = base.PROJECT
WARNING = base.WARNING
FOOTPRINT_NAME = "TI_RPW0010A_HotRodQFN_2x2mm_P0.45mm_TI4225183A_P02"
TI_DRAWING = "TI TPS25946 datasheet SLVSGA8B Rev B pages 45-47; package drawing 4225183/A dated 08/2019"


def layer_set(*layers: int) -> pcbnew.LSET:
    result = pcbnew.LSET()
    for layer in layers:
        result.AddLayer(layer)
    return result


def round_pad(
    footprint: pcbnew.FOOTPRINT,
    number: str,
    x: float,
    y: float,
    sx: float,
    sy: float,
    layers: pcbnew.LSET,
    radius: float = 0.05,
    mask_margin: float | None = None,
) -> pcbnew.PAD:
    pad = pcbnew.PAD(footprint)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(layers)
    pad.SetRoundRectCornerRadius(pcbnew.FromMM(min(radius, sx / 2, sy / 2)))
    if mask_margin is not None:
        pad.SetLocalSolderMaskMargin(pcbnew.FromMM(mask_margin))
    footprint.Add(pad)
    return pad


def add_fab_line(footprint: pcbnew.FOOTPRINT, start: tuple[float, float], end: tuple[float, float]) -> None:
    shape = pcbnew.PCB_SHAPE(footprint)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(pcbnew.VECTOR2I_MM(*start))
    shape.SetEnd(pcbnew.VECTOR2I_MM(*end))
    shape.SetLayer(pcbnew.F_Fab)
    shape.SetWidth(pcbnew.FromMM(0.1))
    footprint.Add(shape)


def create_rpw_footprint(parent=None) -> pcbnew.FOOTPRINT:
    footprint = pcbnew.FOOTPRINT(parent)
    footprint.SetFPID(pcbnew.LIB_ID("ProjectButton_RPW.pretty", FOOTPRINT_NAME))
    footprint.SetValue("TI RPW0010A 4225183/A P0.2 CANDIDATE")
    footprint.SetLibDescription(
        "Project-controlled transcription of TI RPW0010A copper/mask/stencil examples "
        "4225183/A; independent assembler DFM and first-article acceptance remain open."
    )
    copper_mask = layer_set(pcbnew.F_Cu, pcbnew.F_Mask)
    paste = layer_set(pcbnew.F_Paste)

    # Pads 2/3/8/9: 0.60 x 0.25 mm copper at the published 0.45 mm pitch.
    for number, x, y in (
        ("2", -0.9, 0.225), ("3", -0.9, -0.225),
        ("8", 0.9, -0.225), ("9", 0.9, 0.225),
    ):
        round_pad(footprint, number, x, y, 0.6, 0.25, copper_mask, mask_margin=0.05)
        round_pad(footprint, "", x, y, 0.6, 0.25, paste)

    # Pads 5/6: 0.30 x 2.40 mm copper. TI's 0.100 mm stencil example
    # splits each into two 0.28 x 1.06 mm apertures centered at y +/-0.63.
    for number, x in (("5", -0.25), ("6", 0.25)):
        round_pad(footprint, number, x, 0.0, 0.30, 2.40, copper_mask, mask_margin=0.05)
        round_pad(footprint, "", x, 0.63, 0.28, 1.06, paste)
        round_pad(footprint, "", x, -0.63, 0.28, 1.06, paste)

    # Pads 1/4/7/10 are L-shaped. Copper is the union of a 0.60 x
    # 0.30 mm horizontal leg and a 0.25 x 0.65 mm vertical leg. Paste
    # follows TI's reduced 0.60 x 0.275 and 0.225 x 0.63 apertures.
    corners = (
        ("1", -0.9, 0.7, -0.725, 0.875),
        ("4", -0.9, -0.7, -0.725, -0.875),
        ("7", 0.9, -0.7, 0.725, -0.875),
        ("10", 0.9, 0.7, 0.725, 0.875),
    )
    for number, hx, hy, vx, vy in corners:
        round_pad(footprint, number, hx, hy, 0.60, 0.30, copper_mask, mask_margin=0.05)
        round_pad(footprint, number, vx, vy, 0.25, 0.65, copper_mask, mask_margin=0.05)
        round_pad(footprint, "", hx, hy, 0.60, 0.275, paste)
        round_pad(footprint, "", vx, vy, 0.225, 0.63, paste)

    for start, end in (
        ((-1.0, -1.0), (1.0, -1.0)), ((1.0, -1.0), (1.0, 1.0)),
        ((1.0, 1.0), (-1.0, 1.0)), ((-1.0, 1.0), (-1.0, -1.0)),
    ):
        add_fab_line(footprint, start, end)
    marker = pcbnew.PCB_SHAPE(footprint)
    marker.SetShape(pcbnew.SHAPE_T_CIRCLE)
    marker.SetCenter(pcbnew.VECTOR2I_MM(-1.25, 0.8))
    marker.SetEnd(pcbnew.VECTOR2I_MM(-1.15, 0.8))
    marker.SetLayer(pcbnew.F_Fab)
    marker.SetWidth(pcbnew.FromMM(0.1))
    footprint.Add(marker)
    return footprint


original_components = base.components


def components(model):
    items = original_components(model)
    for item in items:
        if item.ref in {"U1", "U1G"}:
            item.footprint = f"ProjectButton_RPW.pretty:{FOOTPRINT_NAME}"
        if item.ref == "U1":
            item.description = (
                "Forward current limiting only. Reverse current is unbounded while ON. "
                "P0.2 corrects the P0.1 RPW land-pattern transcription; independent assembler DFM remains open."
            )
            item.evidence = f"SLVSGA8B Rev B; exact land/stencil transcription from {TI_DRAWING}."
    return items


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


original_release_files = base.release_files


def release_files(items) -> None:
    original_release_files(items)
    footprint_rows = read_csv(RELEASE / "footprint-audit.csv")
    footprint_rows[0].update({
        "footprint": FOOTPRINT_NAME,
        "source": TI_DRAWING,
        "state": "P0.1 DEFECT CORRECTED; INTERNAL TWO-METHOD PARITY PASS; INDEPENDENT/DFM ACCEPTANCE OPEN",
        "evidence_needed": "independent land-pattern audit; assembler DFM; first-article AOI and X-ray",
    })
    write_csv(RELEASE / "footprint-audit.csv", list(footprint_rows[0]), footprint_rows)

    holds = read_csv(RELEASE / "residual-holds.csv")
    for row in holds:
        row["hold_id"] = row["hold_id"].replace("R156-", "R158-")
        if row["hold_id"] == "R158-H01":
            row["state"] = "PARTIAL"
            row["evidence_needed"] = (
                "Internal datasheet/vector parity passed; independent footprint audit, assembler DFM, "
                "stencil-provider acceptance and first-article AOI/X-ray remain required"
            )
    write_csv(RELEASE / "residual-holds.csv", list(holds[0]), holds)

    tests = read_csv(RELEASE / "test-plan.csv")
    for row in tests:
        row["test_id"] = row["test_id"].replace("R156-", "R158-")
    write_csv(RELEASE / "test-plan.csv", list(tests[0]), tests)
    data = read_csv(RELEASE / "test-data-template.csv")
    for row in data:
        row["test_id"] = row["test_id"].replace("R156-", "R158-")
    write_csv(RELEASE / "test-data-template.csv", list(data[0]), data)

    stackup = read_csv(RELEASE / "stackup-and-copper-register.csv")
    for row in stackup:
        if row["item"] == "thermal vias":
            row["candidate"] = "no via-in-pad in P0.2"
    write_csv(RELEASE / "stackup-and-copper-register.csv", list(stackup[0]), stackup)

    parity = [
        ("RPW-001", "side pitch", "0.45", "mm", "0.475", "0.45", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-002", "pads 2/3/8/9 copper", "0.60 x 0.25", "mm", "0.60 x 0.25", "0.60 x 0.25", "PASS"),
        ("RPW-003", "pads 5/6 copper", "0.30 x 2.40", "mm", "0.30 x 1.80", "0.30 x 2.40", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-004", "corner horizontal copper", "0.60 x 0.30", "mm", "0.60 x 0.25", "0.60 x 0.30", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-005", "corner vertical copper", "0.25 x 0.65", "mm", "0.20 x 0.42", "0.25 x 0.65", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-006", "corner vertical center x", "+/-0.725", "mm", "+/-0.620", "+/-0.725", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-007", "pads 5/6 paste", "2 x (0.28 x 1.06)", "mm per copper pad", "full copper 0.30 x 1.80", "2 x (0.28 x 1.06)", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-008", "corner paste horizontal", "0.60 x 0.275", "mm", "full copper", "0.60 x 0.275", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-009", "corner paste vertical", "0.225 x 0.63", "mm", "full copper", "0.225 x 0.63", "P0.1 FAIL / P0.2 PASS"),
        ("RPW-010", "preferred mask expansion", "0.05", "mm nominal candidate", "board default/implicit", "0.05", "P0.2 ENCODED; FABRICATOR TOLERANCE OPEN"),
    ]
    write_csv(
        RELEASE / "rpw-land-pattern-parity.csv",
        ["check_id", "feature", "ti_value", "unit", "p0_1_encoded", "p0_2_encoded", "disposition"],
        [dict(zip(["check_id", "feature", "ti_value", "unit", "p0_1_encoded", "p0_2_encoded", "disposition"], row)) for row in parity],
    )
    status = json.loads((RELEASE / "package-status.json").read_text(encoding="utf-8"))
    status.update({
        "identifier": base.IDENTIFIER,
        "review_round": "R158",
        "configuration_state": "CORRECTED EVALUATION CARRIER REVIEW CANDIDATE",
        "open_holds": 15,
        "partial_holds": 1,
        "p0_1_land_pattern_superseded": True,
    })
    (RELEASE / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (RELEASE / "rpw-parity.svg").write_text(parity_svg(), encoding="utf-8")
    # KiCad 10 emits trailing blanks in review SVGs and progress logs. Normalize
    # them deterministically without changing the rendered content.
    text_outputs = list(RELEASE.rglob("*.svg")) + [RELEASE / "validation" / "kicad-cli.log"]
    for path in text_outputs:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n", encoding="utf-8")


def parity_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 690" role="img" aria-labelledby="t d">
<title id="t">RPW0010A P0.1 defect and P0.2 correction</title><desc id="d">Dimension comparison of the prior and corrected land patterns.</desc>
<rect width="1200" height="690" fill="#f7fbff"/><style>text{{font-family:system-ui,sans-serif;fill:#10233f;font-size:18px}}.h{{font-size:30px;font-weight:800;fill:#082d5b}}.bad{{fill:#ffe4e7;stroke:#8b1e2d;stroke-width:3}}.good{{fill:#dff3ff;stroke:#1557a5;stroke-width:3}}.land{{fill:#f5bd24;stroke:#082d5b;stroke-width:2}}.note{{font-size:16px}}.dim{{stroke:#082d5b;stroke-width:2;marker-start:url(#a);marker-end:url(#a)}}</style>
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 z" fill="#082d5b"/></marker></defs>
<text x="40" y="48" class="h">TI RPW0010A land-pattern correction</text><text x="40" y="78">SLVSGA8B Rev B · drawing 4225183/A · internal parity only</text>
<g transform="translate(55 125)"><rect width="500" height="500" rx="18" class="bad"/><text x="24" y="42" class="h">P0.1 · superseded</text><text x="24" y="75">0.475 mm spacing · 1.80 mm center lands</text>
<g transform="translate(250 270) scale(120)"><rect x="-1.2" y="-.8375" width=".6" height=".25" class="land"/><rect x="-1.2" y="-.3625" width=".6" height=".25" class="land"/><rect x="-.4" y="-.9" width=".3" height="1.8" class="land"/><rect x=".1" y="-.9" width=".3" height="1.8" class="land"/><rect x=".6" y="-.8375" width=".6" height=".25" class="land"/><rect x=".6" y="-.3625" width=".6" height=".25" class="land"/></g>
<text x="24" y="445" class="note">Corner stubs: 0.20 × 0.42 mm at ±0.620 mm</text><text x="24" y="475" class="note">Full-copper paste apertures; no TI 82%/93% stencil split</text></g>
<g transform="translate(645 125)"><rect width="500" height="500" rx="18" class="good"/><text x="24" y="42" class="h">P0.2 · corrected candidate</text><text x="24" y="75">0.45 mm pitch · 2.40 mm center lands</text>
<g transform="translate(250 270) scale(120)"><rect x="-.4" y="-1.2" width=".3" height="2.4" rx=".05" class="land"/><rect x=".1" y="-1.2" width=".3" height="2.4" rx=".05" class="land"/><rect x="-1.2" y="-.35" width=".6" height=".25" rx=".05" class="land"/><rect x="-1.2" y=".1" width=".6" height=".25" rx=".05" class="land"/><path d="M-1.2,-1.2 h.6 v.65 h-.6 z M-1.2,-.85 h.6 v.3 h-.6 z" class="land"/><path d="M.6,-1.2 h.25 v.35 h.35 v.3 h-.6 z" class="land"/><path d="M-1.2,.55 h.6 v.65 h-.25 v-.35 h-.35 z" class="land"/><path d="M.6,.55 h.6 v.3 h-.35 v.35 h-.25 z" class="land"/></g>
<text x="24" y="445" class="note">L copper: 0.60 × 0.30 + 0.25 × 0.65 mm</text><text x="24" y="475" class="note">Separate TI stencil apertures; 0.05 mm mask candidate</text></g>
<text x="55" y="665" class="note">P0.2 remains held for independent audit, assembler DFM, stencil acceptance, AOI/X-ray and physical electrical/thermal tests. {html.escape(WARNING)}</text></svg>'''


def write_readme() -> None:
    (RELEASE / "README.md").write_text(f"""# {base.IDENTIFIER}

**{WARNING}**

R158 corrects the material RPW0010A land-pattern defects found in R156/P0.1. P0.2 encodes TI's 0.45 mm pitch, 2.40 mm central copper, L-shaped corner copper, 0.05 mm mask-expansion candidate and split stencil apertures from drawing 4225183/A.

P0.1 remains historical and is prohibited for supplier use. P0.2 still does not alter the robot baseline, select a fabricator, authorize ordering or release physical work. Internal drawing parity, KiCad ERC/DRC and CAM checks do not replace independent footprint review, assembler/stencil DFM, AOI/X-ray or physical validation.

Generate with KiCad 10 Python:

`\"C:\\Program Files\\KiCad\\10.0\\bin\\python.exe\" tools/generate_hr_v0_dxl_protection_carrier_p02.py`
""", encoding="utf-8")


def write_html() -> None:
    (RELEASE / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R158 corrected RPW carrier</title><style>
:root{{--sky:#9edcff;--deep:#082d5b;--gold:#f5bd24;--paper:#f7fbff;--ink:#10243d;--line:#aac6df}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:18px/1.55 system-ui,sans-serif}}.warning{{background:var(--gold);padding:16px 20px;font-weight:850;border-bottom:4px solid var(--deep)}}header{{background:linear-gradient(135deg,var(--deep),#155b98);color:white;padding:clamp(28px,6vw,70px)}}h1{{font-size:clamp(34px,5vw,62px);line-height:1.05;margin:.3rem 0}}main{{max-width:1200px;margin:auto;padding:24px}}section{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;margin:20px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card{{border-left:8px solid var(--gold);padding:16px;background:#f8fcff}}h2{{font-size:clamp(25px,3vw,38px);color:var(--deep)}}h3{{font-size:22px}}img,iframe{{width:100%;border:2px solid var(--deep);border-radius:10px;background:white}}iframe{{height:760px}}a{{color:#1557a5;font-weight:750}}.meta{{font-size:14px}}@media(max-width:650px){{body{{font-size:16px}}iframe{{height:520px}}}}
</style></head><body><div class="warning">{html.escape(WARNING)}</div><header><div class="meta">PROJECT BUTTON · R158 · {base.IDENTIFIER}</div><h1>RPW footprint corrected.</h1><p>R156's carrier was not fabricable: its side pitch, center lands, corner lands and paste apertures disagreed with TI drawing 4225183/A. P0.2 is the corrected native candidate—not a supplier release.</p></header><main>
<section><h2>Exact disposition</h2><div class="grid"><div class="card"><h3>P0.1 prohibited</h3><p>0.475 mm spacing, 1.80 mm center lands and undersized corner stubs are superseded.</p></div><div class="card"><h3>P0.2 encoded</h3><p>0.45 mm pitch, 2.40 mm center lands, exact L-shaped copper, TI stencil reductions and 0.05 mm mask candidate.</p></div><div class="card"><h3>Hold remains</h3><p>Independent audit, fabricator/stencil DFM, AOI/X-ray and first-article proof remain mandatory.</p></div></div></section>
<section><h2>Dimension comparison</h2><img src="rpw-parity.svg" alt="Comparison of the superseded and corrected RPW land patterns"><p><a href="rpw-land-pattern-parity.csv">Machine-readable parity register</a> · <a href="footprint-audit.csv">Footprint disposition</a> · <a href="residual-holds.csv">Residual holds</a></p></section>
<section><h2>Native source and renders</h2><p><a href="source/{PROJECT}.kicad_pro">KiCad project</a> · <a href="source/{PROJECT}.kicad_pcb">KiCad PCB</a> · <a href="validation/{PROJECT}-erc.rpt">ERC</a> · <a href="validation/{PROJECT}-drc.rpt">DRC</a></p><div class="grid"><img src="output/{PROJECT}-top.png" alt="Corrected P0.2 carrier top render"><img src="output/{PROJECT}-bottom.png" alt="Corrected P0.2 carrier bottom render"></div></section>
<section><h2>Connected schematic</h2><p>The circuit is unchanged from R156; only the physical RPW transcription and related manufacturing evidence changed.</p><iframe title="P0.2 protection carrier schematic" src="output/{PROJECT}-01 Single-channel DXL branch protection core.svg"></iframe></section>
</main></body></html>''', encoding="utf-8")


base.create_rpw_footprint = create_rpw_footprint
base.components = components
base.release_files = release_files
base.write_readme = write_readme
base.write_html = write_html


if __name__ == "__main__":
    raise SystemExit(base.main())
