#!/usr/bin/env python3
"""Generate the R224 web-native review surface for the actual P1.18 KiCad sheets."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
ENG = ROOT / "electrical/reviews/hr-v0-p118-ecad-web-review-p0.1"
OUT = ROOT / "release/hr-v0/ecad-web-review-p1.18-p0.1"
IDENTIFIER = "HR-V0-ECAD-WEB-REVIEW-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

SHEETS = [
    (0, "Project hierarchy and sheet index", "project-button-v3-p1.18-panel-topology-candidate.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate.svg"),
    (1, "External listed sources and DC boundaries", "01_external_sources.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-01 External listed sources and DC boundaries.svg"),
    (2, "Dual-channel E-stop and RESET eligibility", "02_estop_eligibility.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-02 Dual-channel E-stop and RESET eligibility.svg"),
    (3, "Distinct ARM and watchdog-gated SR1 supply", "03_arm_watchdog_eligibility.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-03 Distinct ARM and watchdog-gated SR1 supply.svg"),
    (4, "Contactor coils, mirror contacts and EDM", "04_contactor_edm.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-04 Contactor coils, mirror contacts and EDM.svg"),
    (5, "Redundant actuator-power interruption", "05_actuator_interruption.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-05 Redundant actuator-power interruption.svg"),
    (6, "Protected actuator branches and current-limiter carriers", "06_branches_and_limiters.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-06 Protected actuator branches and current-limiter carriers.svg"),
    (7, "Independent watchdog power, controller and drivers", "07_watchdog_control.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-07 Independent watchdog power, controller and drivers.svg"),
    (8, "Calculated dual-channel 24 V watchdog feedback", "08_watchdog_feedback_interface.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-08 Calculated dual-channel 24 V watchdog feedback.svg"),
    (9, "Compute and control terminals", "09_compute_and_control_terminals.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-09 Compute and control terminals.svg"),
    (10, "U2D2, DXL star, actuator ports and bonding boundary", "10_actuator_interfaces.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-10 U2D2, DXL star, actuator ports and bonding boundary.svg"),
    (11, "Watchdog PCB external connectors", "11_watchdog_pcb_connectors.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-11 Watchdog PCB external connectors.svg"),
    (12, "Watchdog PCB test access", "12_watchdog_pcb_test_access.kicad_sch", "project-button-v3-p1.18-panel-topology-candidate-12 Watchdog PCB test access.svg"),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_csv(directory: Path, name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {name}")
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def svg_geometry(path: Path) -> tuple[str, str, str]:
    head = path.read_text(encoding="utf-8")[:2500]
    width = re.search(r'width="([^"]+)"', head)
    height = re.search(r'height="([^"]+)"', head)
    viewbox = re.search(r'viewBox="([^"]+)"', head)
    if not width or not height or not viewbox:
        raise ValueError(f"missing SVG geometry: {path}")
    return width.group(1), height.group(1), viewbox.group(1)


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    write_csv(directory, "file-manifest.csv", records)


def render_html(sheet_rows: list[dict[str, object]]) -> str:
    web_rows = []
    for row in sheet_rows:
        source = "../../../" + str(row["svg_path"])
        web_rows.append({
            "page": row["page"], "title": row["title"], "svg": quote(source, safe="/.:_-"),
            "sha256": row["svg_sha256"], "bytes": row["svg_bytes"], "native": row["native_sheet_path"],
        })
    data = json.dumps(web_rows, separators=(",", ":"))
    buttons = "".join(
        f'<button type="button" class="sheet-button" data-page="{row["page"]}"><span>{int(row["page"])+1:02d}</span>{html.escape(str(row["title"]))}</button>'
        for row in sheet_rows
    )
    page = fr'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--sky:#e8f6ff;--deep:#073b66;--blue:#0a6da8;--gold:#f4bd28;--paper:#fff;--line:#99c7df;--ink:#082f50}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}header{{background:linear-gradient(120deg,#073b66,#0a6094);color:#fff;border-bottom:7px solid var(--gold);padding:24px}}header>div,main{{max-width:1700px;margin:auto}}.warning{{background:#fff1bd;color:#382a00;border:3px solid var(--gold);padding:13px 16px;font-weight:850}}h1{{font-size:clamp(30px,4.5vw,58px);line-height:1.08;margin:.45rem 0}}h2{{font-size:clamp(22px,2.6vw,36px);line-height:1.15}}p{{max-width:95ch}}main{{padding:22px}}.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px;margin-bottom:20px}}.fact{{background:#fff;border:2px solid var(--line);border-radius:12px;padding:15px}}.fact strong{{display:block;color:var(--blue);font-size:30px}}.notice{{background:#fff;border-left:7px solid var(--gold);padding:15px;margin:16px 0}}.workspace{{display:grid;grid-template-columns:minmax(250px,340px) minmax(0,1fr);gap:16px;align-items:start}}.sidebar,.viewer-card{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:14px}}.sidebar{{position:sticky;top:10px;max-height:calc(100vh - 20px);overflow:auto}}.sidebar label{{font-weight:800}}#sheet-search{{width:100%;font:inherit;min-height:44px;border:2px solid var(--blue);border-radius:8px;padding:8px;margin:6px 0 12px}}.sheet-button{{width:100%;display:grid;grid-template-columns:36px 1fr;gap:8px;text-align:left;align-items:start;border:0;border-bottom:1px solid var(--line);background:#fff;color:var(--ink);font:600 14px/1.35 system-ui,sans-serif;padding:10px 6px;cursor:pointer}}.sheet-button span{{color:var(--blue);font-weight:900}}.sheet-button[aria-current="page"]{{background:#dff2ff;box-shadow:inset 5px 0 var(--gold)}}.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}}.toolbar button,.toolbar a{{font:700 14px/1.2 system-ui,sans-serif;min-height:42px;padding:9px 12px;border:2px solid var(--blue);border-radius:8px;background:#fff;color:var(--deep);text-decoration:none;cursor:pointer}}.toolbar button:hover,.toolbar a:hover{{background:#e3f5ff}}#sheet-title{{margin:.3rem 0;font-size:clamp(22px,2.8vw,36px)}}.meta{{font-size:14px;overflow-wrap:anywhere}}.sheet-frame{{height:min(72vh,900px);min-height:520px;overflow:auto;border:2px solid #6da8c8;background:#f9fcff;border-radius:8px;position:relative}}#sheet-image{{display:block;width:100%;height:auto;max-width:none;transform-origin:top left;background:#fff}}.holds{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:18px}}.hold{{background:#fff;border:2px solid var(--line);border-radius:10px;padding:14px}}footer{{max-width:1700px;margin:auto;padding:22px;font-size:14px;font-weight:700}}@media(max-width:900px){{.workspace{{grid-template-columns:1fr}}.sidebar{{position:static;max-height:330px}}.sheet-frame{{min-height:430px;height:62vh}}}}@media(max-width:520px){{header,main{{padding:15px}}.sheet-frame{{min-height:360px;height:56vh}}.toolbar button,.toolbar a{{width:100%}}}}
</style></head><body><header><div><div class="warning">{WARNING}</div><p>{IDENTIFIER} · R224 · actual KiCad 10 SVG exports</p><h1>Review the connected ECAD in the browser.</h1><p>This viewer presents all 13 native P1.18 schematic sheets. It is a review surface, not a substitute for KiCad source, ERC/netlist checks, physical application review, or configuration acceptance.</p></div></header><main><section class="facts"><div class="fact"><strong>13</strong>native KiCad sheets</div><div class="fact"><strong>0 / 0</strong>ERC errors / warnings</div><div class="fact"><strong>55</strong>two-ended conductor candidates</div><div class="fact"><strong>0</strong>released wires or work steps</div></section><div class="notice"><strong>Configuration boundary:</strong> P1.15 remains current. P1.18 remains an unaccepted topology candidate until independent electrical review and formal configuration disposition.</div><section class="workspace"><aside class="sidebar"><label for="sheet-search">Find a sheet</label><input id="sheet-search" type="search" placeholder="E-stop, watchdog, DXL, terminals">{buttons}</aside><article class="viewer-card"><div class="toolbar"><button id="previous" type="button">Previous sheet</button><button id="next" type="button">Next sheet</button><button type="button" data-zoom="fit">Fit width</button><button type="button" data-zoom="1">100%</button><button type="button" data-zoom="1.5">150%</button><button type="button" data-zoom="2">200%</button><a id="open-svg" href="#" target="_blank" rel="noopener">Open native SVG</a></div><p id="sheet-counter" class="meta"></p><h2 id="sheet-title"></h2><p id="sheet-meta" class="meta"></p><div class="sheet-frame" id="sheet-frame"><img id="sheet-image" alt=""></div></article></section><h2>Acceptance holds</h2><section class="holds"><div class="hold"><strong>Independent ECAD review</strong><p>Terminal/net parity, contact states, cross-references, and the P1.18 change must be independently reviewed.</p></div><div class="hold"><strong>Selections and application</strong><p>Every TBD pin, fuse, conductor, termination, protection, grounding, thermal and accessory selection remains open.</p></div><div class="hold"><strong>Physical evidence</strong><p>Received identity, installation, continuity, polarity, isolation, fault injection and stopping evidence remain unexecuted.</p></div><div class="hold"><strong>Formal configuration</strong><p>This web surface does not promote P1.18 or close an energization gate.</p></div></section></main><footer>{WARNING}</footer><script>
const sheets={data};let current=0;const image=document.querySelector('#sheet-image'),title=document.querySelector('#sheet-title'),counter=document.querySelector('#sheet-counter'),meta=document.querySelector('#sheet-meta'),open=document.querySelector('#open-svg'),frame=document.querySelector('#sheet-frame'),buttons=[...document.querySelectorAll('.sheet-button')];function show(index){{current=(index+sheets.length)%sheets.length;const row=sheets[current];image.src=row.svg;image.alt=`KiCad schematic sheet ${{current+1}} of ${{sheets.length}}: ${{row.title}}`;image.style.width='100%';title.textContent=row.title;counter.textContent=`Sheet ${{current+1}} of ${{sheets.length}}`;meta.textContent=`Native source: ${{row.native}} · SVG bytes: ${{row.bytes}} · SHA-256: ${{row.sha256}}`;open.href=row.svg;buttons.forEach((button,i)=>{{if(i===current)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current')}});frame.scrollTo(0,0);location.hash=`sheet-${{current+1}}`}}buttons.forEach((button,i)=>button.addEventListener('click',()=>show(i)));document.querySelector('#previous').addEventListener('click',()=>show(current-1));document.querySelector('#next').addEventListener('click',()=>show(current+1));document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{{const z=button.dataset.zoom;image.style.width=z==='fit'?'100%':`${{Number(z)*100}}%`;frame.scrollTo(0,0)}}));document.querySelector('#sheet-search').addEventListener('input',event=>{{const q=event.target.value.trim().toLowerCase();buttons.forEach(button=>button.hidden=q&&!button.textContent.toLowerCase().includes(q))}});const requested=Number((location.hash.match(/sheet-(\d+)/)||[])[1]);show(Number.isFinite(requested)&&requested>=1&&requested<=sheets.length?requested-1:0);
</script></body></html>'''
    page = page.replace("</style>", ".workspace.focus{grid-template-columns:1fr}.workspace.focus .sidebar{display:none}</style>")
    page = page.replace('<a id="open-svg"', '<button id="focus" type="button">Focus schematic</button><a id="open-svg"')
    page = page.replace(
        "const requested=",
        "document.querySelector('#focus').addEventListener('click',event=>{const workspace=document.querySelector('.workspace'),focused=workspace.classList.toggle('focus');event.currentTarget.textContent=focused?'Show sheet list':'Focus schematic'});const requested=",
    )
    return page


def main() -> int:
    output_dir = ECAD / "output"
    rows = []
    for page, title, native_name, svg_name in SHEETS:
        native = ECAD / native_name
        svg = output_dir / svg_name
        if not native.is_file() or not svg.is_file():
            raise FileNotFoundError(native if not native.is_file() else svg)
        width, height, viewbox = svg_geometry(svg)
        rows.append({
            "page": page, "title": title,
            "native_sheet_path": native.relative_to(ROOT).as_posix(), "native_sheet_sha256": digest(native),
            "svg_path": svg.relative_to(ROOT).as_posix(), "svg_sha256": digest(svg), "svg_bytes": svg.stat().st_size,
            "width": width, "height": height, "viewbox": viewbox,
            "automated_export_structure": "PASS", "internal_visual_review": "OPEN", "qualified_review": "OPEN",
            "warning": WARNING,
        })
    erc_path = ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate-erc.rpt"
    netlist_path = ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate.net"
    log_path = ECAD / "validation/kicad-cli.log"
    project_path = ECAD / "project-button-v3-p1.18-panel-topology-candidate.kicad_pro"
    sources = []
    for source_id, label, path, fact in (
        ("EWR-SRC-001", "Native KiCad project", project_path, "KiCad project identity and ERC configuration"),
        ("EWR-SRC-002", "Native ERC report", erc_path, "Found 0 violations; ERC messages 0 errors and 0 warnings"),
        ("EWR-SRC-003", "Native netlist", netlist_path, "Machine-readable P1.18 connectivity export"),
        ("EWR-SRC-004", "KiCad CLI log", log_path, "ERC, PDF and thirteen SVG export command evidence"),
    ):
        sources.append({"source_id": source_id, "artifact": label, "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size, "verified_fact": fact, "does_not_establish": "Functional safety, physical correctness, configuration acceptance or work authority", "warning": WARNING})
    holds = [
        ("EWR-H-001", "P1.18 independent schematic review", "OPEN", "Signed pin/net/contact-state/cross-reference and change review"),
        ("EWR-H-002", "P1.15 logic-parity acceptance", "OPEN", "Independent machine and human comparison plus formal disposition"),
        ("EWR-H-003", "TBD and unresolved selections", "OPEN", "Exact received pins, ratings, protection, conductors and order codes"),
        ("EWR-H-004", "electrical application calculations", "OPEN", "Fault, inrush, voltage drop, thermal, fill, grounding and coordination evidence"),
        ("EWR-H-005", "internal full-sheet visual review", "OPEN", "Recorded page-by-page browser inspection with exact findings"),
        ("EWR-H-006", "qualified electrical and functional-safety review", "OPEN", "Named qualified reviewers and signed dispositions"),
        ("EWR-H-007", "received and installed evidence", "NOT EXECUTED", "Identity, continuity, polarity, isolation, torque, pull and fault evidence"),
        ("EWR-H-008", "formal P1.18 configuration promotion", "OPEN", "Accepted immutable revision and merged configuration record"),
    ]
    hold_rows = [{"hold_id": i, "subject": s, "state": st, "closure_evidence": ev, "gate_effect": "NONE - REMAINS OPEN/PARTIAL", "warning": WARNING} for i, s, st, ev in holds]
    authority = [
        {"action": "read, zoom, search, review and redline", "allowed": "TRUE", "boundary": "Internal review only", "warning": WARNING},
        {"action": "promote P1.18", "allowed": "FALSE", "boundary": "Independent review and formal configuration acceptance required", "warning": WARNING},
        {"action": "procure, fabricate, assemble, wire or connect", "allowed": "FALSE", "boundary": "No released physical package exists", "warning": WARNING},
        {"action": "powered test, motion or energization", "allowed": "FALSE", "boundary": "Separate qualified stage authorization required", "warning": WARNING},
    ]
    status = {
        "identifier": IDENTIFIER, "date": "2026-08-11", "round": "R224",
        "ecad_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "current_system_ecad": "V3-P1.15-CARRIER-CANDIDATE",
        "sheet_count": len(rows), "native_sheet_count": len(rows), "svg_export_count": len(rows),
        "erc_errors": 0, "erc_warnings": 0, "structural_export_checks_passed": len(rows),
        "internal_full_sheet_visual_review_complete": False, "independent_review_complete": False,
        "p118_accepted": False, "work_authority": False, "energization_authorized": False,
        "warning": WARNING,
    }
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory, "sheet-register.csv", rows)
        write_csv(directory, "source-hash-register.csv", sources)
        write_csv(directory, "open-holds.csv", hold_rows)
        write_csv(directory, "authority-boundary.csv", authority)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        (directory / "README.md").write_text(
            f"# {IDENTIFIER}\n\n**{WARNING}**\n\nR224 binds every actual P1.18 native sheet to its KiCad SVG export and a web review surface. P1.15 remains current; P1.18 remains unaccepted.\n",
            encoding="utf-8",
        )
    (OUT / "index.html").write_text(render_html(rows), encoding="utf-8")
    manifest(ENG)
    manifest(OUT)
    print(f"Generated {IDENTIFIER}: {len(rows)} native sheets / {len(rows)} bound SVG exports / ERC 0/0")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
