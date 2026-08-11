#!/usr/bin/env python3
"""Generate the R230 P1.19 visual-correction dossier and browser review guide."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
P119 = ROOT / "electrical/kicad/project-button-v3-p1.19-visual-correction-candidate"
OUT = ROOT / "release/hr-v0/p119-visual-correction-p0.1"
ENG = ROOT / "electrical/reviews/hr-v0-p119-visual-correction-p0.1"
IDENTIFIER = "HR-V0-P119-VISUAL-CORRECTION-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"empty CSV prohibited: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse_sexp(path: Path) -> list[object]:
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', path.read_text(encoding="utf-8-sig"))
    stack: list[list[object]] = []
    root: list[object] = []
    current = root
    for token in tokens:
        if token == "(":
            child: list[object] = []
            current.append(child)
            stack.append(current)
            current = child
        elif token == ")":
            current = stack.pop()
        else:
            current.append(json.loads(token) if token.startswith('"') else token)
    if stack:
        raise RuntimeError(f"unbalanced netlist S-expression: {path}")
    return root[0]


def children(block: list[object], name: str) -> list[list[object]]:
    return [item for item in block[1:] if isinstance(item, list) and item and item[0] == name]


def field(block: list[object], name: str) -> str:
    rows = children(block, name)
    return str(rows[0][1]) if rows and len(rows[0]) > 1 else ""


def canonical_netlist(path: Path) -> dict[str, object]:
    root = parse_sexp(path)
    component_sections = children(root, "components")
    net_sections = children(root, "nets")
    if len(component_sections) != 1 or len(net_sections) != 1:
        raise RuntimeError(f"missing component/net sections: {path}")
    components = {}
    for comp in children(component_sections[0], "comp"):
        components[field(comp, "ref")] = {"value": field(comp, "value"), "footprint": field(comp, "footprint")}
    nets = {}
    for net in children(net_sections[0], "net"):
        nodes = []
        for node in children(net, "node"):
            nodes.append((field(node, "ref"), field(node, "pin"), field(node, "pinfunction"), field(node, "pintype")))
        nets[field(net, "name")] = sorted(nodes)
    return {"components": components, "nets": nets}


SHEETS = [
    (0, "project-button-v3-p1.18-panel-topology-candidate.svg", "project-button-v3-p1.19-visual-correction-candidate.svg", "Index", "Overflowing title-block revision/warning and ambiguous P1.15/P1.18 narrative", "Short P1.19 title cells; explicit P1.18-connectivity-preserved subtitle"),
    (1, "project-button-v3-p1.18-panel-topology-candidate-01 External listed sources and DC boundaries.svg", "project-button-v3-p1.19-visual-correction-candidate-01 External listed sources and DC boundaries.svg", "External sources and DC boundaries", "Clipped edge labels; PSA1/JA1 and XD24/XD0 captions/labels collided", "A2 reflow, bounded right column, shortened visible distribution captions"),
    (2, "project-button-v3-p1.18-panel-topology-candidate-02 Dual-channel E-stop and RESET eligibility.svg", "project-button-v3-p1.19-visual-correction-candidate-02 Dual-channel E-stop and RESET eligibility.svg", "E-stop and RESET eligibility", "Edge clipping and dense S0/SR1/S1/XN label fields", "A2 two-row reflow with 170-200 mm column spacing"),
    (3, "project-button-v3-p1.18-panel-topology-candidate-03 Distinct ARM and watchdog-gated SR1 supply.svg", "project-button-v3-p1.19-visual-correction-candidate-03 Distinct ARM and watchdog-gated SR1 supply.svg", "ARM and watchdog gate", "Edge clipping and overlapping KWD interstage labels", "A2 two-row reflow with right column moved inward"),
    (4, "project-button-v3-p1.18-panel-topology-candidate-04 Contactor coils, mirror contacts and EDM.svg", "project-button-v3-p1.19-visual-correction-candidate-04 Contactor coils, mirror contacts and EDM.svg", "Contactor coils and EDM", "Title-block warning/revision overflow", "Bounded title cells and rewrapped notes"),
    (5, "project-button-v3-p1.18-panel-topology-candidate-05 Redundant actuator-power interruption.svg", "project-button-v3-p1.19-visual-correction-candidate-05 Redundant actuator-power interruption.svg", "Actuator-power interruption", "Title-block warning/revision overflow", "Bounded title cells and rewrapped notes"),
    (6, "project-button-v3-p1.18-panel-topology-candidate-06 Protected actuator branches and current-limiter carriers.svg", "project-button-v3-p1.19-visual-correction-candidate-06 Protected actuator branches and current-limiter carriers.svg", "Protected branches", "Title-block overflow; edge labels approached the frame", "Bounded title cells; final labels visually inside the page"),
    (7, "project-button-v3-p1.18-panel-topology-candidate-07 Independent watchdog power, controller and drivers.svg", "project-button-v3-p1.19-visual-correction-candidate-07 Independent watchdog power, controller and drivers.svg", "Watchdog controller and drivers", "UDRV1/RHP1 boxes and WDCTRL1/UDRV2 label fields overlapped", "A2 three-row reflow with isolated controller/driver columns"),
    (8, "project-button-v3-p1.18-panel-topology-candidate-08 Calculated dual-channel 24 V watchdog feedback.svg", "project-button-v3-p1.19-visual-correction-candidate-08 Calculated dual-channel 24 V watchdog feedback.svg", "Watchdog feedback", "Title-block warning/revision overflow", "Bounded title cells and rewrapped notes"),
    (9, "project-button-v3-p1.18-panel-topology-candidate-09 Compute and control terminals.svg", "project-button-v3-p1.19-visual-correction-candidate-09 Compute and control terminals.svg", "Compute and control terminals", "XT1 visible value ran beyond its block; notes entered the title-block region", "Short visible XT1 caption; 90-character note wrap above the frame bottom"),
    (10, "project-button-v3-p1.18-panel-topology-candidate-10 U2D2, DXL star, actuator ports and bonding boundary.svg", "project-button-v3-p1.19-visual-correction-candidate-10 U2D2, DXL star, actuator ports and bonding boundary.svg", "U2D2 and DXL star", "INJ1/J2 labels overlapped and JFRAME caption/terminals were ambiguous", "A2 reflow with isolated actuator column and short JFRAME caption"),
    (11, "project-button-v3-p1.18-panel-topology-candidate-11 Watchdog PCB external connectors.svg", "project-button-v3-p1.19-visual-correction-candidate-11 Watchdog PCB external connectors.svg", "Watchdog PCB connectors", "Title-block warning/revision overflow", "Bounded title cells and rewrapped notes"),
    (12, "project-button-v3-p1.18-panel-topology-candidate-12 Watchdog PCB test access.svg", "project-button-v3-p1.19-visual-correction-candidate-12 Watchdog PCB test access.svg", "Watchdog PCB test access", "Title-block warning/revision overflow", "Bounded title cells and rewrapped notes"),
]


def parity() -> dict[str, object]:
    exact_csv = ["bom.csv", "connector-schedule.csv", "net-schedule.csv", "wire-number-table.csv", "unresolved-selections.csv"]
    csv_rows = {}
    for name in exact_csv:
        a, b = read_csv(P118 / name), read_csv(P119 / name)
        if a != b:
            raise RuntimeError(f"layout-only parity failed for {name}")
        csv_rows[name] = len(a)
    a_net = canonical_netlist(P118 / "validation/project-button-v3-p1.18-panel-topology-candidate.net")
    b_net = canonical_netlist(P119 / "validation/project-button-v3-p1.19-visual-correction-candidate.net")
    if a_net != b_net:
        raise RuntimeError("native netlist semantic parity failed")
    erc = (P119 / "validation/project-button-v3-p1.19-visual-correction-candidate-erc.rpt").read_text(encoding="utf-8-sig")
    if "ERC messages: 0  Errors 0  Warnings 0" not in erc:
        raise RuntimeError("P1.19 ERC is not 0/0")
    return {
        "baseline": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "candidate": "V3-P1.19-VISUAL-CORRECTION-CANDIDATE",
        "component_count": len(a_net["components"]),
        "net_count": len(a_net["nets"]),
        "csv_rows": csv_rows,
        "netlist_semantic_parity": True,
        "erc_errors": 0,
        "erc_warnings": 0,
    }


def html_page(summary: dict[str, object]) -> str:
    options = "".join(f'<option value="{page}">{page:02d} · {html.escape(title)}</option>' for page, _, _, title, _, _ in SHEETS)
    cards = "".join(
        f'<article><span>Sheet {page:02d}</span><h3>{html.escape(title)}</h3><p><strong>Baseline:</strong> {html.escape(finding)}</p><p><strong>Correction:</strong> {html.escape(correction)}</p><p class="pass">Project visual pass recorded</p></article>'
        for page, _, _, title, finding, correction in SHEETS
    )
    data = json.dumps([{"page": p, "old": old, "new": new} for p, old, new, *_ in SHEETS])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.19 visual correction review</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8;--ok:#137333}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(26px,3vw,40px)}}h3{{font-size:20px}}main{{max-width:1500px;margin:auto;padding:28px 18px 64px}}.warning{{background:#fff2bd;color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}label,select,button{{font-size:16px}}select,button{{max-width:100%;padding:10px 14px;border:2px solid var(--blue);border-radius:8px;background:white;color:var(--navy);font-weight:750}}.viewer{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:18px 0 30px}}.viewer.swap figure:first-child{{order:2}}figure{{min-width:0;margin:0;background:white;border:2px solid var(--line);border-radius:12px;overflow:hidden}}figcaption{{padding:12px;background:var(--navy);color:white;font-weight:800}}figure img{{display:block;width:100%;height:68vh;min-height:520px;object-fit:contain}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:12px}}article{{min-width:0;background:white;border:2px solid var(--line);border-radius:12px;padding:16px}}article span{{font-size:14px;font-weight:850;background:var(--sky);padding:5px 8px;border-radius:6px}}.pass{{color:var(--ok);font-weight:850}}a{{color:#075b9c;font-weight:750;overflow-wrap:anywhere}}@media(max-width:900px){{.viewer{{grid-template-columns:1fr}}figure img{{height:58vh;min-height:420px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} · R230</p><h1>Same wiring model. Pages humans can actually review.</h1><p>Interactive P1.18/P1.19 comparison with native KiCad SVGs, sheet-addressable URLs, and explicit project-owned findings.</p></header><main><div class="verdict"><strong>Parity result:</strong> {summary['component_count']} component blocks, {summary['net_count']} native nets, five synchronized schedules, and the native netlist are unchanged. ERC is 0 errors / 0 warnings. P1.19 remains unaccepted.</div><label for="sheet">Sheet</label> <select id="sheet">{options}</select> <button id="swap" type="button">Swap sides</button><div class="viewer" id="viewer"><figure><figcaption>Baseline P1.18</figcaption><img id="old" alt="Baseline P1.18 native KiCad sheet"></figure><figure><figcaption>Corrected P1.19 candidate</figcaption><img id="new" alt="Corrected P1.19 native KiCad sheet"></figure></div><h2>Recorded findings and corrections</h2><div class="grid">{cards}</div><div class="warning">This is a project-owned visual and semantic-parity review, not independent electrical review, functional-safety validation, fabrication release, connection authority, or permission to energize.</div><p><a href="sheet-review.csv">Sheet review register</a> · <a href="parity-summary.json">Parity summary</a> · <a href="open-holds.csv">Open holds</a> · <a href="../../../electrical/kicad/project-button-v3-p1.19-visual-correction-candidate/output/project-button-v3-p1.19-visual-correction-candidate-preliminary.pdf">Native KiCad PDF</a></p></main><script>const rows={data};const sel=document.querySelector('#sheet'),oldImg=document.querySelector('#old'),newImg=document.querySelector('#new'),viewer=document.querySelector('#viewer');function show(){{const r=rows[Number(sel.value)];oldImg.src='../../../electrical/kicad/project-button-v3-p1.18-panel-topology-candidate/output/'+encodeURIComponent(r.old);newImg.src='../../../electrical/kicad/project-button-v3-p1.19-visual-correction-candidate/output/'+encodeURIComponent(r.new);history.replaceState(null,'','?sheet='+r.page)}}sel.addEventListener('change',show);document.querySelector('#swap').addEventListener('click',()=>viewer.classList.toggle('swap'));const q=Number(new URLSearchParams(location.search).get('sheet'));if(Number.isInteger(q)&&q>=0&&q<rows.length)sel.value=String(q);show();</script></body></html>'''


def main() -> int:
    summary = parity()
    OUT.mkdir(parents=True, exist_ok=True)
    ENG.mkdir(parents=True, exist_ok=True)
    rows = []
    for page, old_svg, new_svg, title, finding, correction in SHEETS:
        old_path = P118 / "output" / old_svg
        new_path = P119 / "output" / new_svg
        if not old_path.is_file() or not new_path.is_file():
            raise RuntimeError(f"missing native SVG pair for page {page}")
        rows.append({
            "page": str(page), "title": title,
            "p118_svg": old_path.relative_to(ROOT).as_posix(), "p118_sha256": digest(old_path),
            "p119_svg": new_path.relative_to(ROOT).as_posix(), "p119_sha256": digest(new_path),
            "baseline_visual_finding": finding, "correction": correction,
            "review_viewport_px": "1680x1188", "project_visual_result": "PASS",
            "independent_review": "OPEN", "qualified_electrical_review": "OPEN", "warning": WARNING,
        })
    write_csv(OUT / "sheet-review.csv", rows)
    write_csv(ENG / "sheet-review.csv", rows)
    holds = [
        ("VIS-H-001", "Independent native-sheet review", "Independent reviewer disposition of all thirteen P1.19 sheets and exports"),
        ("VIS-H-002", "Qualified electrical review", "Terminal/net/function review against the accepted safety requirements and physical implementation"),
        ("VIS-H-003", "Functional-safety allocation and validation", "Accepted PLr/SIL allocation, CCF analysis, stopping budget, validation plan and executed evidence"),
        ("VIS-H-004", "Physical panel and harness", "Released placement, routes, lengths, conductors, terminations, protection, enclosure and received/installed inspection"),
        ("VIS-H-005", "Unresolved selections", "Close every controlled SELECTION REQUIRED record with current primary evidence and application acceptance"),
        ("VIS-H-006", "Pre-power evidence", "Released limits, calibrated instruments, executed continuity/isolation/backfeed/absence-of-voltage results and signed disposition"),
        ("VIS-H-007", "Configuration promotion", "Formal authority decision before P1.19 can supersede current P1.15"),
    ]
    hold_rows = [{"hold_id": i, "subject": s, "status": "OPEN", "evidence_needed": e, "warning": WARNING} for i, s, e in holds]
    write_csv(OUT / "open-holds.csv", hold_rows)
    write_csv(ENG / "open-holds.csv", hold_rows)
    summary.update({
        "identifier": IDENTIFIER, "round": "R230", "date": "2026-08-11",
        "native_sheet_pairs_reviewed": 13, "project_visual_passes": 13, "open_holds": len(holds),
        "p115_current": True, "p118_accepted": False, "p119_accepted": False,
        "independent_review_complete": False, "qualified_electrical_review_complete": False,
        "functional_safety_approved": False, "fabrication_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False,
        "motion_authorized": False, "energization_authorized": False, "warning": WARNING,
    })
    for directory in (OUT, ENG):
        (directory / "parity-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR230 records a project-owned page-by-page visual pass and exact semantic parity from P1.18 to the unaccepted P1.19 layout-correction candidate. Seven external/physical/configuration holds remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(html_page(summary), encoding="utf-8", newline="\n")
    doc = f"""# HR-V0 P1.19 visual-correction dossier P0.1

> **{WARNING}**

Identifier: `{IDENTIFIER}`
Round: R230
Date: 2026-08-11

## Outcome

The native P1.18 electrical package was not visually reviewable as released: all title blocks overflowed; sheets 01-03 clipped or collided labels; sheet 07 overlapped controller/driver content; sheet 09 allowed notes and the XT1 caption to exceed their intended regions; and sheet 10 overlapped the DXL-star and actuator-port label fields.

P1.19 is a new unaccepted layout-only candidate. P1.18 remains immutable. Five dense pages (01, 02, 03, 07 and 10) use A2; the other child pages remain A3. Title-block fields are bounded, the full preliminary warning remains a prominent native text item on every page, and exact values remain in the hidden KiCad `Value` fields/BOM where selected visible captions were shortened.

## Machine parity

- 84 component blocks unchanged.
- 106 native nets unchanged.
- 82 BOM rows, 340 connector/terminal rows, 106 net-schedule rows, 301 wire-table rows and 63 unresolved-selection rows are exactly equal between P1.18 and P1.19.
- Native KiCad netlist component/value/footprint and net-node membership are equal.
- KiCad 10.0.5 ERC: 0 errors / 0 warnings.

## Visual review

All thirteen native SVG exports were inspected at a 1680 x 1188 review viewport. The final P1.19 exports received thirteen project-owned visual passes. The browser surface supports sheet selection, side-by-side P1.18/P1.19 comparison, direct native SVG rendering and mobile reflow. This is not independent or qualified review.

## Configuration boundary

P1.15 remains the current electrical configuration. P1.18 and P1.19 are unaccepted supporting candidates. P1.19 cannot supersede P1.15 without independent and qualified electrical disposition plus formal configuration authority.

## Open holds

Seven holds remain in `release/hr-v0/p119-visual-correction-p0.1/open-holds.csv`: independent native-sheet review, qualified electrical review, functional-safety allocation/validation, physical panel/harness definition, unresolved selections, executed pre-power evidence and configuration promotion.

No procurement, fabrication, assembly, connection, powered test, motion or energization authority is created.
"""
    (ROOT / "docs/hr-v0-p119-visual-correction-p0.1.md").write_text(doc, encoding="utf-8", newline="\n")
    request = f"""# R230 independent electrical review request

> **{WARNING}**

Review `V3-P1.19-VISUAL-CORRECTION-CANDIDATE` against immutable P1.18 and current P1.15. This request is for design accuracy and completeness, not approval to build or energize.

Please:

1. Open all thirteen native KiCad sheets and native SVG exports.
2. Confirm the P1.18-to-P1.19 component, terminal, wire-table, schedule and netlist semantic-parity evidence independently.
3. Check every page for clipped or overlapping symbols, net labels, wire numbers, notes, warnings and title-block fields at practical review zoom.
4. Verify that shortened visible captions do not conceal or alter the exact `Value`, BOM, datasheet, terminal or net identities.
5. Review the safety-chain, watchdog, contactor, actuator-power interruption, grounding, branch, DXL-star and test-access content for electrical accuracy and completeness.
6. Reconcile the 18 BLOCKER / 30 MAJOR / 8 MINOR Sol R12 baseline without treating later project-owned work as independently accepted.
7. Return exact sheet/reference/net findings and state whether P1.19 is ready for qualified electrical and functional-safety review.

Keep P1.15 current unless formal configuration authority promotes a successor. Do not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
"""
    (ROOT / "docs/reviews/2026-08-11-r230-independent-review-request.md").write_text(request, encoding="utf-8", newline="\n")
    gate_rows = [
        {"round": "R230", "gate_id": "EG-002", "status": "partial", "evidence_added": IDENTIFIER, "remaining_evidence": "independent and qualified P1.19 review; accepted ECAD promotion; physical panel/harness evidence", "authority_added": "NO", "warning": WARNING},
        {"round": "R230", "gate_id": "EG-004", "status": "partial", "evidence_added": IDENTIFIER, "remaining_evidence": "released protection/grounding/termination design; executed pre-power and fault evidence; qualified disposition", "authority_added": "NO", "warning": WARNING},
        {"round": "R230", "gate_id": "EG-020", "status": "partial", "evidence_added": IDENTIFIER, "remaining_evidence": "accepted wiring baseline, physical continuity/isolation/backfeed results and signed release", "authority_added": "NO", "warning": WARNING},
    ]
    write_csv(ROOT / "requirements/hr-v0-gate-evidence-supplement-r230.csv", gate_rows)
    release_path = ROOT / "release/hr-v0/release-candidate.json"
    release_data = json.loads(release_path.read_text(encoding="utf-8-sig"))
    electrical = next(item for item in release_data["current_products"] if item["domain"] == "electrical")
    for support in ("V3-P1.19-VISUAL-CORRECTION-CANDIDATE", IDENTIFIER):
        if support not in electrical["supporting_identifiers"]:
            electrical["supporting_identifiers"].append(support)
    electrical["release_state"] = "p115_current_p118_p119_unaccepted_r230_visual_and_semantic_parity_complete_qualified_disposition_physical_selections_tests_and_authority_open"
    electrical["panel_visual_correction_candidate"] = "V3-P1.19-VISUAL-CORRECTION-CANDIDATE"
    electrical["p119_visual_correction_dossier"] = IDENTIFIER
    electrical["p119_visual_correction_summary"] = "84 components, 106 native nets and five synchronized schedules unchanged; 13 project visual passes; P1.19 remains unaccepted"
    release_path.write_text(json.dumps(release_data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
