#!/usr/bin/env python3
"""Generate the R238 consolidated P1.21 native-KiCad review surface."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P119 = ROOT / "electrical/kicad/project-button-v3-p1.19-visual-correction-candidate"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
OUT = ROOT / "release/hr-v0/p121-consolidated-review-p0.1"
REVIEW = ROOT / "electrical/reviews/hr-v0-p121-consolidated-review-p0.1"
IDENTIFIER = "HR-V0-P121-CONSOLIDATED-REVIEW-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def terminal_delta() -> list[dict[str, object]]:
    fields = ("sheet", "reference", "terminal")
    old = {tuple(row[field] for field in fields): row for row in read_csv(P119 / "connector-schedule.csv")}
    new = {tuple(row[field] for field in fields): row for row in read_csv(P121 / "connector-schedule.csv")}
    result = []
    for key in sorted(old):
        before, after = old[key], new[key]
        if (before["pin_name"], before["net"]) != (after["pin_name"], after["net"]):
            result.append({
                "sheet": key[0], "reference": key[1], "terminal": key[2],
                "p119_pin_name": before["pin_name"], "p119_net": before["net"],
                "p121_pin_name": after["pin_name"], "p121_net": after["net"],
                "disposition": "INTENTIONAL - move the ordinary series watchdog supply gate from SR1:A1 to downstream SRA1:A1",
                "warning": WARNING,
            })
    return result


def svg_rows() -> list[dict[str, object]]:
    baseline = read_csv(ROOT / "electrical/reviews/hr-v0-p119-visual-correction-p0.1/sheet-review.csv")
    svgs = sorted((P121 / "output").glob("*.svg"))
    result = []
    for page in range(13):
        if page == 0:
            matches = [p for p in svgs if p.name == f"{P121.name}.svg"]
        else:
            matches = [p for p in svgs if p.name.startswith(f"{P121.name}-{page:02d} ")]
        if len(matches) != 1:
            raise RuntimeError(f"P1.21 page {page}: expected one SVG, found {len(matches)}")
        prior = baseline[page]
        paper = "A2" if page in {1, 2, 3, 7, 10} else ("A3" if page else "A4")
        result.append({
            "page": page, "title": prior["title"], "paper": paper,
            "p119_visual_result": prior["project_visual_result"],
            "p121_svg": matches[0].relative_to(ROOT).as_posix(),
            "p121_sha256": sha(matches[0]),
            "layout_basis": "P1.19 generator inherited transitively through P1.20 into P1.21",
            "p121_visual_disposition": "PROJECT_REVIEW_REQUIRED_AFTER_LOGIC_CHANGE" if page in {2, 3} else "INHERITED_LAYOUT_SOURCE_CHECKED",
            "independent_review": "OPEN", "qualified_electrical_review": "OPEN", "warning": WARNING,
        })
    return result


def page(layout: list[dict[str, object]], delta: list[dict[str, object]]) -> str:
    options = "".join(f'<option value="{i}">Page {row["page"]}: {html.escape(str(row["title"]))}</option>' for i, row in enumerate(layout))
    image_data = json.dumps(["../../../" + str(row["p121_svg"]) for row in layout])
    delta_rows = "".join(
        f"<tr><td><strong>{html.escape(str(r['reference']))}:{html.escape(str(r['terminal']))}</strong></td>"
        f"<td><code>{html.escape(str(r['p119_net']))}</code></td><td><code>{html.escape(str(r['p121_net']))}</code></td>"
        f"<td>{html.escape(str(r['p121_pin_name']))}</td></tr>" for r in delta
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 consolidated native-KiCad review</title><style>
:root{{--sky:#82d4f6;--navy:#082b4c;--blue:#155d91;--gold:#f3b61f;--paper:#f5fbff;--line:#8eb3ca}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif;background:#fff}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.04;max-width:20ch;margin:.35rem 0 1rem}}h2{{font-size:clamp(1.4rem,2.2vw,2.1rem)}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:700}}.lead{{font-size:clamp(1.15rem,1.8vw,1.5rem);max-width:76rem}}.status{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}}.card{{border:3px solid var(--blue);border-radius:.8rem;padding:1rem;background:var(--paper)}}.card strong{{display:block;font-size:1.35rem}}label{{display:block;font-weight:700;margin:.8rem 0 .35rem}}select{{width:100%;font:inherit;padding:.75rem;border:3px solid var(--blue);border-radius:.55rem;background:#fff}}.viewer{{margin:1rem 0;border:3px solid var(--navy);border-radius:.8rem;overflow:auto;background:#eef6fa;min-height:480px}}.viewer img{{display:block;width:100%;min-width:900px;height:auto}}.table{{overflow:auto;border:2px solid var(--line);border-radius:.7rem;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b7ccd8}}th{{background:var(--navy);color:#fff}}code{{font-size:14px;white-space:normal}}@media(max-width:700px){{.viewer{{min-height:300px}}}}
</style></head><body><header><strong>{IDENTIFIER} / R238</strong><h1>One candidate, all thirteen native sheets</h1><div class="warning">{WARNING}</div></header><main><p class="lead">P1.21 is already the consolidated source-level review candidate. It inherits P1.19's readable layout and explicit panel topology, then moves the ordinary watchdog series gate from SR1 power to downstream SRA1 power. P1.15 remains current. P1.21 remains unaccepted and this page does not authorize work.</p><div class="status"><div class="card"><strong>13 native pages</strong>Root plus twelve child sheets</div><div class="card"><strong>84 components</strong>Identity count unchanged</div><div class="card"><strong>106 named nets</strong>Count unchanged</div><div class="card"><strong>6 keyed terminals</strong>Intentional P1.19 to P1.21 semantic delta</div><div class="card"><strong>ERC 0 / 0</strong>Connectivity/annotation only</div></div><h2>Native-sheet viewer</h2><label for="sheet">Choose a sheet</label><select id="sheet">{options}</select><div class="viewer"><img id="drawing" alt="Selected P1.21 native KiCad sheet"></div><p>Pages 2 and 3 require fresh project and independent visual review because the logic changed after P1.19. The other page layouts are source-inherited, not independently approved.</p><h2>Exact P1.19 → P1.21 terminal delta</h2><div class="table"><table><thead><tr><th>Terminal</th><th>P1.19 net</th><th>P1.21 net</th><th>P1.21 role</th></tr></thead><tbody>{delta_rows}</tbody></table></div><h2>What remains open</h2><p>Manufacturer application acceptance, protected routing, received-component inspection, no-load restart/brownout traces, fault injection, stopping and guard evidence, PLr/SIL allocation, qualified electrical and functional-safety review, configuration promotion and signed work authorization all remain open.</p></main><script>const files={image_data};const select=document.querySelector('#sheet');const drawing=document.querySelector('#drawing');function show(){{drawing.src=files[Number(select.value)];drawing.alt=select.options[select.selectedIndex].text+' — P1.21 native KiCad export';}}select.addEventListener('change',show);show();</script></body></html>'''


def main() -> None:
    for directory in (OUT, REVIEW):
        directory.mkdir(parents=True, exist_ok=True)
    delta = terminal_delta()
    if len(delta) != 6:
        raise RuntimeError(f"expected six P1.19-to-P1.21 keyed terminal changes, found {len(delta)}")
    layout = svg_rows()
    lineage = [
        {"sequence": 1, "candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "generator": "tools/generate_hr_v0_electrical_v3_p118_panel_topology_candidate.py", "contribution": "explicit XD24/XD0/XN1/XN2/XN3 topology nodes", "accepted": "NO", "warning": WARNING},
        {"sequence": 2, "candidate": "V3-P1.19-VISUAL-CORRECTION-CANDIDATE", "generator": "tools/generate_hr_v0_electrical_v3_p119_visual_correction_candidate.py", "contribution": "readable A2/A3 layout, bounded labels and title blocks", "accepted": "NO", "warning": WARNING},
        {"sequence": 3, "candidate": "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE", "generator": "tools/generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate.py", "contribution": "intermediate separate-input watchdog experiment", "accepted": "NO", "warning": WARNING},
        {"sequence": 4, "candidate": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "generator": "tools/generate_hr_v0_electrical_v3_p121_sra1_supply_watchdog_candidate.py", "contribution": "preferred consolidated review candidate; KWD series-gates only SRA1:A1", "accepted": "NO", "warning": WARNING},
    ]
    holds_text = [
        "Fresh page-by-page project visual inspection of P1.21 pages 2 and 3",
        "Independent terminal-by-terminal and every-sheet review",
        "Qualified electrical and functional-safety review",
        "Pilz and Phoenix written application disposition",
        "Released protected routing and separation",
        "Received-component identity and terminal verification",
        "Authorized no-load restart, brownout and chatter traces",
        "Authorized single/dual/common-cause fault injection",
        "Measured stopping and released guard evidence",
        "PLr/SIL/category/CCF/DC/reliability allocation and validation",
        "Formal configuration promotion and separately signed work authorization",
    ]
    holds = [{"hold_id": f"P121C-H{i:02d}", "closure_evidence": text, "state": "OPEN", "warning": WARNING} for i, text in enumerate(holds_text, 1)]
    counts = {name: len(read_csv(P121 / name)) for name in ("bom.csv", "connector-schedule.csv", "net-schedule.csv", "wire-number-table.csv", "unresolved-selections.csv")}
    status = {
        "identifier": IDENTIFIER, "round": "R238", "date": "2026-08-11",
        "current_candidate": "V3-P1.15-CARRIER-CANDIDATE",
        "consolidated_review_candidate": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
        "p121_accepted": False, "native_sheets": 13, "components": 84, "named_nets": 106,
        "schedule_rows": counts, "p119_to_p121_keyed_terminal_changes": 6,
        "erc_errors": 0, "erc_warnings": 0, "erc_scope": "CONNECTIVITY_AND_ANNOTATION_ONLY",
        "independent_review_complete": False, "qualified_review_complete": False,
        "functional_safety_approved": False, "work_authority": False, "open_holds": len(holds), "warning": WARNING,
    }
    sources = [
        P121 / "project-button-v3-p1.21-sra1-supply-watchdog-candidate.kicad_pro",
        P121 / "project-button-v3-p1.21-sra1-supply-watchdog-candidate.kicad_sch",
        P121 / "connector-schedule.csv", P121 / "net-schedule.csv", P121 / "wire-number-table.csv",
        P121 / "validation/project-button-v3-p1.21-sra1-supply-watchdog-candidate-erc.rpt",
        ROOT / "tools/generate_hr_v0_electrical_v3_p119_visual_correction_candidate.py",
        ROOT / "tools/generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate.py",
        ROOT / "tools/generate_hr_v0_electrical_v3_p121_sra1_supply_watchdog_candidate.py",
    ]
    source_rows = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size, "warning": WARNING} for p in sources]
    datasets = {
        "lineage-register.csv": (("sequence", "candidate", "generator", "contribution", "accepted", "warning"), lineage),
        "sheet-review-register.csv": (("page", "title", "paper", "p119_visual_result", "p121_svg", "p121_sha256", "layout_basis", "p121_visual_disposition", "independent_review", "qualified_electrical_review", "warning"), layout),
        "terminal-delta.csv": (("sheet", "reference", "terminal", "p119_pin_name", "p119_net", "p121_pin_name", "p121_net", "disposition", "warning"), delta),
        "source-register.csv": (("path", "sha256", "bytes", "warning"), source_rows),
        "open-holds.csv": (("hold_id", "closure_evidence", "state", "warning"), holds),
    }
    for directory in (OUT, REVIEW):
        for name, (fields, rows) in datasets.items():
            write_csv(directory / name, fields, rows)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR238 proves that P1.21 is the single consolidated native-KiCad review candidate. It inherits the P1.19 layout and panel-node work and changes six keyed terminals to gate SRA1:A1. P1.15 remains current; P1.21 remains unaccepted.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(layout, delta), encoding="utf-8", newline="\n")
    manifest = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        manifest.append({"file": path.name, "size_bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", ("file", "size_bytes", "sha256", "warning"), manifest)
    print(f"Wrote {IDENTIFIER}: 13 sheets, 6 keyed terminal changes, {len(holds)} open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
