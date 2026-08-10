#!/usr/bin/env python3
"""Generate the R185 HR-V0 Q4X box physical-layout candidate."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/q4x-box-layout-p0.1"
CAD = ROOT / "cad/hr-v0-q4x-box-layout-p0.1"
WEB = ROOT / "release/hr-v0/q4x-box-layout-p0.1"
DOC = ROOT / "docs/hr-v0-q4x-box-layout-p0.1.md"
FORM = ROOT / "tests/forms/hr-v0-q4x-box-layout-inspection-p0.1.csv"
WARNING = "PRELIMINARY - DIMENSIONAL REVIEW CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
IDENTIFIER = "HR-V0-Q4X-BOX-LAYOUT-P0.1"
DATE = "2026-08-10"


def write_csv(path: Path, header: list[str], rows: list[tuple[object, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


SOURCES = [
    ("QLS-001", "Hammond Manufacturing", "PJ1084T official product page", "live page; checked 2026-08-10", "https://www.hammfg.com/part/PJ1084T", "exact enclosure identity and current download routes"),
    ("QLS-002", "Hammond Manufacturing", "PJ1084T dimensional drawing", "issue 2014-06-04; checked 2026-08-10", "https://www.hammfg.com/files/parts/pdf/PJ1084T.pdf?v=1697661964", "overall, inner-panel, usable-depth and mounting dimensions"),
    ("QLS-003", "Hammond Manufacturing", "PJ1084T STEP", "download stamp 1697662030; checked 2026-08-10", "https://www.hammfg.com/files/parts/stp/PJ1084T.zip?v=1697662030", "catalog geometry inspection only; no manufacturing tolerance inferred"),
    ("QLS-004", "Hammond Manufacturing", "14F0907 official product page", "live page; checked 2026-08-10", "https://www.hammfg.com/part/14F0907", "exact fiberglass-panel identity"),
    ("QLS-005", "Hammond Manufacturing", "14F0907 dimensional drawing", "issue 2020-01-29; checked 2026-08-10", "https://www.hammfg.com/files/parts/pdf/14F0907.pdf?v=1697661935", "panel size, thickness and four-hole pattern"),
    ("QLS-006", "Hammond Manufacturing", "14F0907 STEP", "download stamp 1697661987; checked 2026-08-10", "https://www.hammfg.com/files/parts/stp/14F0907.zip?v=1697661987", "174.498 x 222.250 x 3.175 mm catalog solid"),
    ("QLS-007", "Phoenix Contact", "NS 35/7,5 PERF 500MM item 1207650", "live page; checked 2026-08-10", "https://www.phoenixcontact.com/en-pc/products/din-rail-perforated-ns-35-75-perf-500mm-1207650", "35 x 7.5 mm rail, 15 x 6.2 mm holes at 25 mm pitch, catalog tolerances"),
    ("QLS-008", "Phoenix Contact", "PTCB E1 24DC/0.1A NO item 1464484", "live page; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/electronic-circuit-breaker-ptcb-e1-24dc-01a-no-1464484", "6.2 x 105.8 x 55.6 mm catalog envelope"),
    ("QLS-009", "Phoenix Contact", "PT 2,5 item 3209510 product data", "generated 2026-07-12; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-3209510?type=pdf", "5.2 mm width; 48.6 mm height; 36.8 mm depth on NS 35/7.5"),
    ("QLS-010", "Phoenix Contact", "PT 2,5-QUATTRO item 3209578 product data", "generated 2026-06-27; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/multi-conductor-terminal-block-pt-25-quattro-3209578?type=pdf", "5.2 mm width; 72.2 mm height; 36.8 mm depth on NS 35/7.5"),
    ("QLS-011", "Phoenix Contact", "CLIPFIX 35 item 3022218 product data", "generated 2026-07-02; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/end-block-clipfix-35-3022218?type=pdf", "9.5 mm installed width and 54.6 x 33.5 mm catalog envelope"),
    ("QLS-012", "Phoenix Contact", "D-ST 2,5 / D-ST 2,5-QUATTRO", "live/generated pages; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/end-cover-d-st-25-3030417", "2.2 mm width for each exact cover candidate"),
    ("QLS-013", "LAPP", "SKINTOP ST-M item 53111000 data sheet", "DB53111000EN version 17; valid 2023-06-20; checked 2026-08-10", "https://dam-media.lapp.com/9/917/91782/32f1ce4e45eb4b69b2dd28b70730b82a.pdf", "M12x1.5, 15 mm wrench, 16.6 mm body diameter, 8 mm thread, 3.5-7 mm cable range"),
    ("QLS-014", "LAPP", "SKINTOP GMP-GL-M item 53119000 data sheet", "DB53119000EN version 09; valid 2019-02-19; checked 2026-08-10", "https://imager.lapp.com/e/lapp/IxNMTvvLiYtWEfUsJRUaNg~~/DB53119000EN.pdf", "M12x1.5 locknut, 17 mm wrench, 18.7 mm corner envelope and 5 mm thickness"),
]


DIMENSIONS = [
    ("QLD-001", "PANEL1 overall X", "174.498", "mm", "14F0907 drawing 6.87 in and official STEP", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-002", "PANEL1 overall Y", "222.250", "mm", "14F0907 drawing 8.75 in and official STEP", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-003", "PANEL1 thickness", "3.175", "mm", "14F0907 drawing 0.13 nominal; official STEP 3.175", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-004", "PANEL1 hole diameter", "6.350", "mm", "14F0907 drawing 0.25 in TYP (4)", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-005", "PANEL1 hole-center X span", "158.750", "mm", "14F0907 drawing 6.25 in", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-006", "PANEL1 hole-center Y span", "209.550", "mm", "14F0907 drawing 8.25 in", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-007", "DR1 rail cut length", "150.000", "mm", "project candidate; above Phoenix 100 mm perforated-rail minimum", "DIMENSION CANDIDATE / CUT NOT RELEASED"),
    ("QLD-008", "DR1 profile width", "35.000", "mm", "Phoenix 1207650 current product data", "CATALOG BOUND / NOT RELEASED"),
    ("QLD-009", "device-group catalog width sum", "60.800", "mm", "2x9.5 + 6.2 + 6x5.2 + 2x2.2", "ARITHMETIC SCREEN / INSTALLED FIT OPEN"),
    ("QLD-010", "rail-end to panel-edge nominal clearance", "12.249", "mm", "(174.498 - 150.000) / 2", "NOMINAL SCREEN / TOLERANCE OPEN"),
    ("QLD-011", "device-group to panel-edge nominal clearance", "56.849", "mm", "(174.498 - 60.800) / 2", "NOMINAL SCREEN / ORIENTATION OPEN"),
    ("QLD-012", "max-device envelope to panel Y edge", "58.225", "mm", "222.250 / 2 - 105.800 / 2", "SYMMETRIC PLANNING SCREEN ONLY"),
    ("QLD-013", "G1/G2 gland connection thread", "M12x1.5", "thread", "LAPP DB53111000EN version 17", "CATALOG BOUND / BORE NOT RELEASED"),
    ("QLD-014", "G1/G2 gland thread length", "8.000", "mm", "LAPP DB53111000EN version 17", "CATALOG BOUND / WALL STACK OPEN"),
    ("QLD-015", "G1/G2 gland body diameter", "16.600", "mm", "LAPP DB53111000EN version 17", "CATALOG BOUND / SPACING OPEN"),
    ("QLD-016", "G1/G2 locknut thickness", "5.000", "mm", "LAPP DB53119000EN version 09", "CATALOG BOUND / STACK OPEN"),
    ("QLD-017", "G1/G2 enclosure bore", "SELECTION REQUIRED", "mm", "not published as an application bore by the checked LAPP records", "NO DRILLING VALUE RELEASED"),
]


LAYOUT = [
    ("QLP-001", "PANEL1 datum", "panel geometric center", "X right; Y up; Z out of panel toward enclosure lid", "REVIEW DATUM / NOT FABRICATION DATUM"),
    ("QLP-002", "PANEL1 hole H1", "X=-79.375 mm; Y=+104.775 mm", "diameter 6.350 mm", "CATALOG HOLE / VERIFY RECEIVED"),
    ("QLP-003", "PANEL1 hole H2", "X=+79.375 mm; Y=+104.775 mm", "diameter 6.350 mm", "CATALOG HOLE / VERIFY RECEIVED"),
    ("QLP-004", "PANEL1 hole H3", "X=-79.375 mm; Y=-104.775 mm", "diameter 6.350 mm", "CATALOG HOLE / VERIFY RECEIVED"),
    ("QLP-005", "PANEL1 hole H4", "X=+79.375 mm; Y=-104.775 mm", "diameter 6.350 mm", "CATALOG HOLE / VERIFY RECEIVED"),
    ("QLP-006", "DR1 rail envelope", "X=-75.000..+75.000 mm; Y=-17.500..+17.500 mm", "centered horizontal 150 x 35 mm candidate", "PLACEMENT CANDIDATE / NOT RELEASED"),
    ("QLP-007", "device group envelope", "X=-30.400..+30.400 mm", "60.800 mm catalog-width sum centered on DR1", "ARITHMETIC ENVELOPE / ORIENTATION OPEN"),
    ("QLP-008", "DR1 mounting points", "SELECTION REQUIRED", "choose from received rail slots after actual first-hole offset and tolerance are measured", "NO PANEL DRILLING COORDINATES RELEASED"),
    ("QLP-009", "G1/G2 entry axes", "SELECTION REQUIRED", "received flat-wall/rib survey, wrench access, wall stack, bend radius and separation required", "NO ENCLOSURE DRILLING COORDINATES RELEASED"),
]


HOLDS = [
    ("QLH-001", "received panel", "verify identity, 174.498 x 222.250 x 3.175 mm catalog envelope, four-hole pattern, flatness and enclosure fit"),
    ("QLH-002", "received enclosure", "map usable bottom-wall flats, ribs, bosses, hinge/latch/feet zones, local wall thickness and closed-lid clearance"),
    ("QLH-003", "rail cut", "receive 1207650, record first/last slot centers and catalog-tolerance realization, select cut datum, cut/deburr/protect edges and inspect 150.0 mm result"),
    ("QLH-004", "rail mounting hardware", "select exact screw, nut, washers and retention method compatible with 6.2 mm slots and 3.175 mm fiberglass panel; set torque from qualified application review"),
    ("QLH-005", "device installation", "confirm PTCB/terminal orientation, end-cover side/count, CLIPFIX retention, marker access and installed 60.8 mm width"),
    ("QLH-006", "gland bores", "obtain manufacturer/application bore allowance or qualify the received gland/hole stack; freeze diameter, tolerance, edge finish and tool"),
    ("QLH-007", "gland coordinates", "freeze G1/G2 axes only after received-wall survey, tool access, cable separation, bend radius and no-interference review"),
    ("QLH-008", "gland torque", "obtain current LAPP application torque for the exact body/locknut/housing stack or a qualified alternate installation process"),
    ("QLH-009", "completed enclosure", "review loss of catalog enclosure rating after modification; define labels, strain relief, ingress, thermal and service-access acceptance"),
    ("QLH-010", "grounding/isolation", "qualified Boston review of isolated metal rail in nonmetal enclosure; verify no unintended PE, 0 V, drain, chassis or robot-domain connection"),
    ("QLH-011", "work authority", "issue separate signed authorization for receiving/metrology before any later cutting or drilling scope"),
    ("QLH-012", "qualified review", "qualified mechanical/electrical reviewers accept the final drilling drawing, hardware stack and inspection plan"),
]


def panel_svg() -> str:
    # ViewBox is drafting space, not millimetres. All dimensions are emitted as text.
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1040 760' role='img' aria-labelledby='title desc'>
<title id='title'>HR-V0 Q4X box panel layout candidate</title><desc id='desc'>Dimensioned fiberglass panel, mounting holes, centered DIN rail and 60.8 millimetre device group planning envelope.</desc>
<style>text{{font-family:system-ui,sans-serif;fill:#102033;font-size:16px}}.small{{font-size:14px}}.dim{{stroke:#1469a8;stroke-width:2;fill:none}}.panel{{fill:#dff4ff;stroke:#092f63;stroke-width:3}}.rail{{fill:#e8edf2;stroke:#4b5968;stroke-width:3}}.group{{fill:#f5bf27;fill-opacity:.72;stroke:#765800;stroke-width:3}}.hole{{fill:#fff;stroke:#092f63;stroke-width:3}}.held{{fill:#fff2bd;stroke:#8a6700;stroke-width:2;stroke-dasharray:9 7}}.label{{font-weight:750}}.warn{{fill:#6a1b1b;font-weight:800}}</style>
<rect width='1040' height='760' fill='#f7fbff'/><text x='40' y='42' class='label' style='font-size:24px'>HR-V0-Q4X-BOX-LAYOUT-P0.1 · PANEL VIEW</text><text x='40' y='70' class='warn'>PRELIMINARY · NO DRILLING OR FABRICATION RELEASE</text>
<rect class='panel' x='282' y='110' width='436.245' height='555.625' rx='2'/>
<circle class='hole' cx='301.875' cy='126.063' r='7.94'/><circle class='hole' cx='698.750' cy='126.063' r='7.94'/><circle class='hole' cx='301.875' cy='649.563' r='7.94'/><circle class='hole' cx='698.750' cy='649.563' r='7.94'/>
<rect class='rail' x='312.5' y='344.0' width='375' height='87.5'/><rect class='group' x='424' y='255.5' width='152' height='264.5'/>
<line class='dim' x1='282' y1='92' x2='718.245' y2='92'/><line class='dim' x1='282' y1='82' x2='282' y2='102'/><line class='dim' x1='718.245' y1='82' x2='718.245' y2='102'/><text x='451' y='84' class='label'>174.498 mm</text>
<line class='dim' x1='748' y1='110' x2='748' y2='665.625'/><line class='dim' x1='738' y1='110' x2='758' y2='110'/><line class='dim' x1='738' y1='665.625' x2='758' y2='665.625'/><text x='770' y='395' class='label' transform='rotate(90 770 395)'>222.250 mm</text>
<line class='dim' x1='301.875' y1='684' x2='698.750' y2='684'/><line class='dim' x1='301.875' y1='674' x2='301.875' y2='694'/><line class='dim' x1='698.750' y1='674' x2='698.750' y2='694'/><text x='448' y='712' class='label'>158.750 mm hole centres</text>
<line class='dim' x1='264' y1='126.063' x2='264' y2='649.563'/><line class='dim' x1='254' y1='126.063' x2='274' y2='126.063'/><line class='dim' x1='254' y1='649.563' x2='274' y2='649.563'/><text x='238' y='446' class='label' transform='rotate(-90 238 446)'>209.550 mm hole centres</text>
<text x='324' y='330' class='label'>DR1 · 150.000 × 35.000 mm · centred</text><text x='434' y='283' class='label'>60.800 mm</text><text x='436' y='306'>catalog-width</text><text x='446' y='329'>envelope</text>
<text x='40' y='144' class='label'>DATUM</text><text x='40' y='169'>panel geometric centre</text><text x='40' y='194'>+X right · +Y up</text><text x='40' y='219'>review coordinates only</text>
<rect class='held' x='790' y='475' width='220' height='160' rx='10'/><text x='810' y='505' class='label'>HELD</text><text x='810' y='535'>rail fastener coordinates</text><text x='810' y='560'>gland bore diameter</text><text x='810' y='585'>gland coordinates</text><text x='810' y='610'>torque + rating after cuts</text>
<text x='40' y='742' class='small'>Catalog geometry must be verified on received parts. Symmetric envelopes do not define installed wire exits or terminal orientation.</text></svg>"""


def entry_svg() -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1040 520' role='img' aria-labelledby='title2 desc2'>
<title id='title2'>Q4X enclosure entry decision boundary</title><desc id='desc2'>The exact gland envelope is known, while the enclosure bore and coordinates remain selection required.</desc>
<style>text{{font-family:system-ui,sans-serif;fill:#102033;font-size:16px}}.box{{fill:#dff4ff;stroke:#092f63;stroke-width:3}}.known{{fill:#f5bf27;stroke:#765800;stroke-width:3}}.held{{fill:#fff2bd;stroke:#8a6700;stroke-width:3;stroke-dasharray:10 8}}.arrow{{stroke:#1469a8;stroke-width:4;fill:none;marker-end:url(#m)}}.label{{font-weight:800}}.warn{{fill:#6a1b1b;font-weight:800}}</style><defs><marker id='m' markerWidth='8' markerHeight='8' refX='7' refY='3' orient='auto'><path d='M0,0 L0,6 L8,3 z' fill='#1469a8'/></marker></defs>
<rect width='1040' height='520' fill='#f7fbff'/><text x='40' y='44' class='label' style='font-size:24px'>ENCLOSURE ENTRY DECISION</text><text x='40' y='74' class='warn'>NO HOLE DIAMETER OR LOCATION IS RELEASED</text>
<rect class='known' x='50' y='125' width='260' height='235' rx='14'/><text x='75' y='160' class='label'>KNOWN FROM LAPP</text><text x='75' y='195'>53111000 gland</text><text x='75' y='223'>M12×1.5 thread</text><text x='75' y='251'>8 mm thread length</text><text x='75' y='279'>Ø16.6 mm body</text><text x='75' y='307'>3.5–7 mm cable range</text><text x='75' y='335'>53119000 nut: 5 mm thick</text>
<path class='arrow' d='M320 242 H400'/><rect class='held' x='410' y='125' width='260' height='235' rx='14'/><text x='435' y='160' class='label'>SELECTION REQUIRED</text><text x='435' y='195'>through-bore diameter</text><text x='435' y='223'>bore tolerance + finish</text><text x='435' y='251'>wall thickness + ribs</text><text x='435' y='279'>tool + wrench clearance</text><text x='435' y='307'>G1/G2 coordinates</text><text x='435' y='335'>installation torque</text>
<path class='arrow' d='M680 242 H760'/><rect class='box' x='770' y='125' width='220' height='235' rx='14'/><text x='795' y='160' class='label'>EVIDENCE TO CLOSE</text><text x='795' y='195'>received-part survey</text><text x='795' y='223'>manufacturer response</text><text x='795' y='251'>qualified drill drawing</text><text x='795' y='279'>trial coupon/process</text><text x='795' y='307'>inspection + retention</text><text x='795' y='335'>completed-box review</text>
<text x='50' y='425'>Hammond permits punching, cutting and drilling the component enclosure, but that does not define this project's safe hole or preserve the finished assembly rating.</text><text x='50' y='455' class='label'>R185 stops at the evidence boundary instead of converting an M12 thread label into an invented drill instruction.</text></svg>"""


def write_package() -> None:
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "document", "revision_or_date", "official_locator", "controlled_use"], SOURCES)
    write_csv(PKG / "dimension-register.csv", ["dimension_id", "feature", "value", "unit", "basis", "state"], DIMENSIONS)
    write_csv(PKG / "panel-layout.csv", ["record_id", "feature", "coordinate_or_extent", "detail", "state"], LAYOUT)
    write_csv(PKG / "closure-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)
    write_csv(PKG / "vendor-file-hashes.csv", ["record_id", "vendor_file", "sha256", "storage_rule"], [
        ("QLV-001", "PJ1084T.pdf", "6575E4ED98516487B7F3D15AB17ECF9DE0F085F8EDF13A421E3CAE3F9F415BF4", "verified temporary download; official URL retained, vendor file not redistributed"),
        ("QLV-002", "PJ1084T.step", "794D143FF3BE4364106AC9907977878B68AFBD4872AC47D21CAAF696B062966F", "verified temporary download; official URL retained, vendor file not redistributed"),
        ("QLV-003", "14F0907.pdf", "F4865CD4FA7C3153ED00AD9A681E76B4F04DC03646942C5A08220702796E061A", "verified temporary download; official URL retained, vendor file not redistributed"),
        ("QLV-004", "14F0907.stp", "B756FACBF0BDB9FABEBF7AD09D5394519470A2F4D35AA0CEAE05D846E7E666E6", "verified temporary download; official URL retained, vendor file not redistributed"),
        ("QLV-005", "DB53111000EN-v17.pdf", "88CC075C3C009AC059ABA1D1AE4C021DF5454A7573DAD6DC7E47CB78F85EE938", "verified temporary download; official URL retained, vendor file not redistributed"),
        ("QLV-006", "DB53119000EN-v09.pdf", "30D6331FCDEE9A8CB8BF179411166A40BDD30B48EBAABBCB0C54FD413A1C7676", "verified temporary download; official URL retained, vendor file not redistributed"),
    ])
    status = {
        "identifier": IDENTIFIER,
        "round": "R185",
        "date": DATE,
        "status": WARNING,
        "source_records": len(SOURCES),
        "dimension_records": len(DIMENSIONS),
        "layout_records": len(LAYOUT),
        "open_holds": len(HOLDS),
        "released_drill_holes": 0,
        "released_fasteners": 0,
        "authorized_procurement": 0,
        "authorized_fabrication": 0,
        "authorized_connection": 0,
        "authorized_energization": 0,
        "safety_function_credit": "ZERO",
        "correction": "14F0907 short side corrected from R184 174.75 mm to 174.498 mm catalog geometry",
        "gate_effect": {"EG-025": "OPEN", "EG-026": "PARTIAL"},
    }
    PKG.mkdir(parents=True, exist_ok=True)
    (PKG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_csv(FORM, ["inspection_id", "article", "check", "nominal_or_question", "measured_or_answered", "evidence_uri", "inspector", "result", "disposition"], [
        ("QLI-001", "14F0907", "identity and damage", "exact part and intact fiberglass", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-002", "14F0907", "overall X/Y/thickness", "174.498 / 222.250 / 3.175 mm catalog geometry", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-003", "14F0907", "four-hole pattern", "Ø6.350 on 158.750 x 209.550 mm centers", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-004", "PJ1084T", "panel fit and supplied screws", "four-point fit without stress or interference", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-005", "PJ1084T", "bottom-wall survey", "flat zones, ribs, bosses, feet, hinge/latch and local wall thickness", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-006", "1207650", "received perforation pattern", "15 x 6.2 mm slots at 25 mm pitch; record realized first/last centers", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-007", "DR1", "cut/edge condition", "150.000 mm candidate; burr-free; edge protection selected", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-008", "device group", "installed width and orientation", "60.800 mm catalog-width sum; actual recorded", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-009", "G1/G2", "bore/stack/torque", "all remain SELECTION REQUIRED", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
        ("QLI-010", "completed closed box", "clearance/retention/isolation", "no contact; no unintended bond; labels readable", "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD"),
    ])


def write_docs_and_web() -> None:
    CAD.mkdir(parents=True, exist_ok=True)
    (CAD / "panel-layout.svg").write_text(panel_svg(), encoding="utf-8")
    (CAD / "enclosure-entry-decision.svg").write_text(entry_svg(), encoding="utf-8")
    DOC.write_text(f"""# HR-V0 Q4X box physical-layout candidate P0.1

> **{WARNING}**

Artifact: **{IDENTIFIER}**

Round: **R185**

Date: **{DATE}**

## Outcome

R185 converts R184's incomplete enclosure-layout row into a dimensioned panel-layout candidate and a precise drilling hold. It corrects the `14F0907` short side from the R184 value of 174.75 mm to the manufacturer drawing/STEP value of 174.498 mm. The panel is represented as 174.498 x 222.250 x 3.175 mm with four 6.350 mm catalog holes on 158.750 x 209.550 mm centers.

The proposed 150.000 mm Phoenix `1207650` rail is centered on the panel. Its nominal end clearance is 12.249 mm per side. Two `CLIPFIX 35` brackets, one 6.2 mm PTCB, six 5.2 mm terminal bodies and two 2.2 mm end covers sum to a 60.800 mm catalog-width envelope, leaving 56.849 mm nominal panel-edge clearance per side when centered. These are arithmetic and catalog-geometry screens, not installed-fit proof.

## Why the gland holes remain blank

LAPP publishes the exact `53111000` M12x1.5 gland geometry, 8 mm thread length, 16.6 mm body diameter and 3.5-7 mm cable range. It also publishes the `53119000` M12x1.5 locknut as 17 mm across flats, 18.7 mm across corners and 5 mm thick. The checked manufacturer records do not publish a Project Button through-bore tolerance or safe coordinate through the molded `PJ1084T` wall.

R185 therefore releases no bore diameter and no G1/G2 coordinates. The received enclosure must be surveyed for flat wall, ribs, bosses, feet, hinge/latch interference and local thickness. The received rail must likewise establish the realized slot offset before fastener coordinates exist. Qualified mechanical/electrical review must then accept the drilling drawing, hardware stack, torque, edge treatment, ingress/thermal consequences and inspection plan.

## Controlled artifacts

- dimension, source, layout, vendor-hash and hold registers: `test-equipment/hr-v0/q4x-box-layout-p0.1/`;
- review-native SVGs and proxy CAD source: `cad/hr-v0-q4x-box-layout-p0.1/`;
- blank received-article inspection form: `tests/forms/hr-v0-q4x-box-layout-inspection-p0.1.csv`; and
- interactive guide: `release/hr-v0/q4x-box-layout-p0.1/index.html`.

## Review effect

All twelve `QLH-*` holds remain open. R185 closes no Sol R12 blocker, no energization gate and no physical-work authorization. `EG-025` remains open and `EG-026` remains partial. The package provides a better review target; it is not a drill template or assembly instruction.
""", encoding="utf-8")

    source_rows = "".join(f"<tr><td>{escape(s[0])}</td><td>{escape(s[1])}</td><td><a href='{escape(s[4])}'>{escape(s[2])}</a></td><td>{escape(s[3])}</td><td>{escape(s[5])}</td></tr>" for s in SOURCES)
    dim_rows = "".join(f"<tr><td>{escape(d[0])}</td><td>{escape(d[1])}</td><td>{escape(d[2])} {escape(d[3])}</td><td>{escape(d[4])}</td><td>{escape(d[5])}</td></tr>" for d in DIMENSIONS)
    hold_cards = "".join(f"<article><p class='tag'>{escape(h[0])}</p><h3>{escape(h[1])}</h3><p>{escape(h[2])}</p></article>" for h in HOLDS)
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENTIFIER}</title><style>
:root{{--sky:#dff4ff;--blue:#092f63;--mid:#1469a8;--gold:#f5bf27;--ink:#102033;--paper:#f7fbff;--line:#8bb6d3}}*{{box-sizing:border-box}}html,body{{max-width:100%}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper);overflow-x:hidden}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1240px;margin:auto;padding:clamp(18px,4vw,48px)}}h1{{font-size:clamp(36px,6vw,70px);line-height:1.05;color:var(--blue);margin:.3rem 0;overflow-wrap:anywhere}}h2{{font-size:clamp(26px,3vw,40px);color:var(--blue);margin-top:2.4rem}}h3{{font-size:18px;color:var(--blue)}}.lead{{font-size:20px;max-width:920px}}.warn{{background:#fff2bd;border:3px solid #765800;padding:18px;font-weight:800;color:#473400;overflow-wrap:anywhere}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:16px}}.metric,article,.decision{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #d3eaf7}}.metric strong{{display:block;color:var(--blue);font-size:30px}}.tag,.badge{{display:inline-block;max-width:100%;font-size:14px;font-weight:800;background:var(--gold);color:#17253b;border-radius:999px;padding:6px 10px;white-space:normal;overflow-wrap:anywhere}}.viewer{{max-width:100%;background:#fff;border:2px solid var(--line);border-radius:14px;padding:12px;overflow:auto}}.viewer img{{display:block;min-width:900px;width:100%;height:auto}}.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}button{{font:inherit;font-weight:750;border:2px solid var(--blue);background:#fff;color:var(--blue);padding:10px 14px;border-radius:9px;cursor:pointer}}button[aria-selected='true']{{background:var(--blue);color:#fff}}.diagram{{display:none}}.diagram.active{{display:block}}.table-wrap{{max-width:100%;overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:980px;background:#fff}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #c6dce9;font-size:14px}}th{{background:var(--blue);color:#fff}}footer{{margin-top:36px;padding:24px;background:var(--blue);color:#fff;overflow-wrap:anywhere}}@media(max-width:720px){{header,main{{padding:18px}}.lead{{font-size:18px}}}}
</style></head><body><header><span class='badge'>R185 · DIMENSIONED PHYSICAL-LAYOUT CANDIDATE</span><h1>The panel now has coordinates. The enclosure still has no drill instruction.</h1><p class='lead'>Manufacturer drawings and STEP geometry correct the panel size, lock the catalog hole pattern, and prove a centered rail/device envelope fits arithmetically. Received-part and qualified-review evidence still control every new hole.</p></header><main><p class='warn'>{escape(WARNING)}</p>
<section class='metrics'><div class='metric'><strong>174.498 × 222.250</strong>mm panel geometry</div><div class='metric'><strong>150.000</strong>mm centered rail candidate</div><div class='metric'><strong>60.800</strong>mm catalog device-group width</div><div class='metric'><strong>0</strong>released drill holes</div></section>
<section><h2>Interactive dimensional guide</h2><div class='tabs'><button aria-selected='true' data-target='panel'>Panel + rail</button><button aria-selected='false' data-target='entry'>Enclosure entry boundary</button></div><div class='viewer'><div id='panel' class='diagram active'><img src='../../../cad/hr-v0-q4x-box-layout-p0.1/panel-layout.svg' alt='Dimensioned panel and rail layout'></div><div id='entry' class='diagram'><img src='../../../cad/hr-v0-q4x-box-layout-p0.1/enclosure-entry-decision.svg' alt='Known gland geometry and held enclosure drilling inputs'></div></div></section>
<section><h2>The correction that matters</h2><div class='decision'><strong>R184's 174.75 mm panel short side is superseded.</strong> Hammond's 2020-01-29 drawing states 6.87 in and the official STEP measures 174.498 mm. R185 uses that geometry throughout. The PJ1084T drawing's rounded optional-panel callout is not used to overwrite the part-specific panel drawing and solid.</div></section>
<section><h2>Exact catalog and derived dimensions</h2><div class='table-wrap'><table><thead><tr><th>ID</th><th>Feature</th><th>Value</th><th>Basis</th><th>State</th></tr></thead><tbody>{dim_rows}</tbody></table></div></section>
<section><h2>Twelve holds prevent physical work</h2><div class='grid'>{hold_cards}</div></section>
<section><h2>Primary manufacturer evidence</h2><div class='table-wrap'><table><thead><tr><th>ID</th><th>Maker</th><th>Document</th><th>Revision/date</th><th>Controlled use</th></tr></thead><tbody>{source_rows}</tbody></table></div></section>
<section><h2>Sol R12 disposition</h2><p>Sol's 18 BLOCKER / 30 MAJOR / 8 MINOR verdict remains the independent baseline. This project-owned pass supplies one missing physical-definition layer but closes no blocker, no functional-safety allocation, no physical verification and no energization gate.</p></section></main><footer>{escape(WARNING)}</footer><script>document.querySelectorAll('button[data-target]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('button[data-target]').forEach(x=>x.setAttribute('aria-selected','false'));document.querySelectorAll('.diagram').forEach(x=>x.classList.remove('active'));b.setAttribute('aria-selected','true');document.getElementById(b.dataset.target).classList.add('active')}}));</script></body></html>"""
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    write_package()
    write_docs_and_web()
    print(f"generated {IDENTIFIER}: {len(DIMENSIONS)} dimensions, {len(HOLDS)} open holds, 0 drill releases")


if __name__ == "__main__":
    main()
