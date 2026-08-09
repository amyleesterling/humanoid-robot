"""Generate the R161 carrier-integrated ECAD, panel, and harness boundary package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "integration" / "hr-v0-dxl-carrier-integration-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-carrier-integration-p0.1"
IDENTIFIER = "HR-V0-DXL-CARRIER-INTEGRATION-P0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
ELEC = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"
STAR = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star-p0.2-carrier-candidate"
CARRIER = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3"
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6"
SOURCES = {
    "electrical/kicad/project-button-v3-p1.15-carrier-candidate/connector-schedule.csv": ELEC / "connector-schedule.csv",
    "electrical/kicad/project-button-v3-p1.15-carrier-candidate/net-schedule.csv": ELEC / "net-schedule.csv",
    "electrical/kicad/project-button-v3-p1.15-carrier-candidate/validation/project-button-v3-p1.15-carrier-candidate.net": ELEC / "validation" / "project-button-v3-p1.15-carrier-candidate.net",
    "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/connector-schedule.csv": STAR / "connector-schedule.csv",
    "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb": STAR / "hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb",
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv": CARRIER / "terminal-schedule.csv",
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/hr-v0-dxl-protection-carrier-p0.3.kicad_pcb": CARRIER / "hr-v0-dxl-protection-carrier-p0.3.kicad_pcb",
    "electrical/panel/hr-v0-control-panel-p0.6/backplate-layout.csv": PANEL / "backplate-layout.csv",
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
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


def reset_dir(path: Path, expected_parent: Path) -> None:
    if path.exists():
        resolved = path.resolve()
        if resolved.parent != expected_parent.resolve() or resolved.name != path.name:
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    path.mkdir(parents=True)


def main() -> None:
    for source in SOURCES.values():
        if not source.is_file():
            raise FileNotFoundError(source)
    reset_dir(ENG, ROOT / "electrical" / "integration")
    reset_dir(OUT, ROOT / "release" / "hr-v0")

    net_rows = []
    for axis in (1, 2, 3):
        net_rows.extend([
            {"axis": f"J{axis}", "stage": "1_PROTECTION_OUTPUT", "reference_terminal": f"F{axis}.2", "net": f"J{axis}_FUSED_PRELIMIT", "next_reference_terminal": f"LIM{axis}.JIN1:1", "state": "CONNECTED IN V3-P1.15 CANDIDATE", "warning": WARNING},
            {"axis": f"J{axis}", "stage": "2_LIMITER_INPUT", "reference_terminal": f"LIM{axis}.JIN1:1", "net": f"J{axis}_FUSED_PRELIMIT", "next_reference_terminal": f"LIM{axis}.JOUT1:1", "state": "P0.3 CARRIER CANDIDATE; PHYSICAL ARTICLE ABSENT", "warning": WARNING},
            {"axis": f"J{axis}", "stage": "3_LIMITER_OUTPUT", "reference_terminal": f"LIM{axis}.JOUT1:1", "net": f"J{axis}_LIMITED_VDD", "next_reference_terminal": f"INJ1.PWR{axis}:1", "state": "CONNECTED IN V3-P1.15 CANDIDATE", "warning": WARNING},
            {"axis": f"J{axis}", "stage": "4_STAR_INPUT", "reference_terminal": f"DXL-STAR JP{axis}.1", "net": f"J{axis}_LIMITED_VDD", "next_reference_terminal": f"DXL-STAR JA{axis}.2", "state": "ROUTED IN DXL-STAR-P0.2 CANDIDATE", "warning": WARNING},
            {"axis": f"J{axis}", "stage": "5_ACTUATOR_PORT", "reference_terminal": f"J{axis}.2", "net": f"J{axis}_LIMITED_VDD", "next_reference_terminal": "ACTUATOR VDD", "state": "CONNECTED IN V3-P1.15 CANDIDATE; HARNESS/PHYSICAL EVIDENCE OPEN", "warning": WARNING},
        ])
    write_csv(ENG / "net-transition-matrix.csv", net_rows)

    placements = [
        ("LIM1", 54.0, 538.0, "J1 shoulder P0.3 variant"),
        ("LIM2", 164.0, 538.0, "J2 elbow P0.3 variant"),
        ("LIM3", 54.0, 608.0, "G1 gripper P0.3 variant"),
    ]
    placement_rows = []
    for index, (ref, x, y, role) in enumerate(placements, 1):
        placement_rows.append({"placement_id": f"CIP-{index:03d}", "reference": ref, "role": role, "x_mm": f"{x:.1f}", "y_mm": f"{y:.1f}", "width_mm": "100.0", "height_mm": "60.0", "reserved_parent": "P0.6 BP-026 OPEN-LOWER-ZONE x=54..377.8 y=533.4..675.8", "boundary_result": "ANALYTICAL PASS", "overlap_result": "ANALYTICAL PASS", "release_state": "PLACEMENT CANDIDATE - NO DRILLING", "required_evidence": "received backplate and board dimensions; standoffs; connector sweep; depth; airflow; service access; qualified layout review", "warning": WARNING})
    write_csv(ENG / "panel-placement-screen.csv", placement_rows)

    hole_rows = []
    relative_holes = (("MH1", 5.0, 5.0), ("MH2", 95.0, 5.0), ("MH3", 5.0, 55.0), ("MH4", 95.0, 55.0))
    for ref, x, y, _ in placements:
        for hole, hx, hy in relative_holes:
            hole_rows.append({"carrier_reference": ref, "hole_reference": hole, "board_relative_x_mm": f"{hx:.1f}", "board_relative_y_mm": f"{hy:.1f}", "candidate_backplate_x_mm": f"{x + hx:.1f}", "candidate_backplate_y_mm": f"{y + hy:.1f}", "hole_diameter_mm": "3.2 BOARD NPTH; backplate hole/fastener SELECTION REQUIRED", "release_state": "COORDINATE CANDIDATE - DO NOT DRILL", "warning": WARNING})
    write_csv(ENG / "mounting-hole-screen.csv", hole_rows)

    route_data = [
        ("HAR-CIN-J1", "F1/F2/F3 service-envelope center (104,450) used only as a geometric surrogate", "LIM1 center (104,568)", 118.0, "direct centerline lower bound"),
        ("HAR-CIN-J2", "F1/F2/F3 service-envelope center (104,450) used only as a geometric surrogate", "LIM2 center (214,568)", 228.0, "direct centerline lower bound"),
        ("HAR-CIN-G1", "F1/F2/F3 service-envelope center (104,450) used only as a geometric surrogate", "LIM3 center (104,638)", 188.0, "direct centerline lower bound"),
        ("HAR-COUT-J1", "LIM1 center (104,568)", "DXL-STAR center (274,260)", 630.0, "shorter screened route via WD1 center x=28"),
        ("HAR-COUT-J2", "LIM2 center (214,568)", "DXL-STAR center (274,260)", 627.6, "shorter screened route via WD2 center x=403.8"),
        ("HAR-COUT-G1", "LIM3 center (104,638)", "DXL-STAR center (274,260)", 700.0, "shorter screened route via WD1 center x=28"),
    ]
    route_rows = [{"route_id": rid, "from_basis": start, "to_basis": end, "geometric_screen_mm": f"{distance:.1f}", "screen_method": method, "cut_length_mm": "SELECTION REQUIRED", "why_not_a_cut_length": "surrogate centers omit exact connector/terminal locations, duct entry/exit, bend radius, service loop, strain relief, termination allowance and received tolerances", "release_state": "ROUTE SCREEN ONLY - DO NOT CUT", "warning": WARNING} for rid, start, end, distance, method in route_data]
    write_csv(ENG / "route-bound-screen.csv", route_rows)

    source_rows = [
        {"source_id": "CIS-001", "source": "Electrical V3-P1.15 carrier candidate", "revision_or_date": "generated 2026-08-09; KiCad 10.0.5", "uri": "../kicad/project-button-v3-p1.15-carrier-candidate/", "controlled_fact": "F1/F2/F3 pre-limiter rails and LIM1/LIM2/LIM3 post-limiter rails are distinct across 13 native pages", "not_proved": "physical wiring, fabrication or safety function", "warning": WARNING},
        {"source_id": "CIS-002", "source": "DXL-STAR-P0.2 carrier candidate", "revision_or_date": "generated 2026-08-09; KiCad 10.0.5", "uri": "../kicad/hr-v0-dxl-star-p0.2-carrier-candidate/", "controlled_fact": "JP1/JP2/JP3 and JA1/JA2/JA3 use only J1/J2/J3_LIMITED_VDD; routed geometry is otherwise controlled against P0.1", "not_proved": "fabrication, connector-current or physical no-backfeed behavior", "warning": WARNING},
        {"source_id": "CIS-003", "source": "P0.3 carrier native source", "revision_or_date": "R159 controlled source", "uri": "../kicad/hr-v0-dxl-protection-carrier-p0.3/", "controlled_fact": "100 x 60 mm nominal outline; MH1..MH4 at (5,5), (95,5), (5,55), (95,55); JIN1/JOUT1 pin 1 positive and pin 2 return", "not_proved": "received dimensions, DFM, assembly or electrical performance", "warning": WARNING},
        {"source_id": "CIS-004", "source": "Control panel P0.6 backplate layout", "revision_or_date": "current planning candidate", "uri": "../panel/hr-v0-control-panel-p0.6/backplate-layout.csv", "controlled_fact": "nominal 533.4 x 685.8 mm backplate and BP-026 lower reserve x=54..377.8, y=533.4..675.8", "not_proved": "received fit, depth, mounting holes, thermal or enclosure-system approval", "warning": WARNING},
    ]
    write_csv(ENG / "source-register.csv", source_rows)

    unresolved = [
        "received backplate and all three carrier board dimensions",
        "exact carrier standoffs, fasteners, hole tolerances, edge distances, coating preparation and bonding disposition",
        "connector body and mated-harness sweep, depth, cover closure and service clearance",
        "exact F1/F2/F3 holder terminal identities and source-side harness terminations",
        "exact connector/terminal coordinates, duct entries, bend radii, service loops and cut lengths",
        "JST strip/crimp process, approved tooling, inspection, pull and retention criteria",
        "wire/connector/fuse/source current, voltage-drop, inrush, fault, regeneration, ambient, bundling and thermal coordination",
        "P0.3 PCBA DFM, assembly process, first article and three physical variants",
        "DXL-STAR-P0.2 manufacturing data, DFM, first article and received no-copper U2D2 VDD proof",
        "continuity, polarity, isolation, no-backfeed, reverse-energy and fault-injection evidence",
        "DXL waveform, error-rate, EMC and separation from actuator-current conductors",
        "qualified electrical, mechanical-layout and functional-safety review plus separate written work authority",
    ]
    unresolved_rows = [{"selection_id": f"CIU-{i:03d}", "topic": topic, "state": "SELECTION REQUIRED", "evidence_uri": "", "warning": WARNING} for i, topic in enumerate(unresolved, 1)]
    write_csv(ENG / "unresolved-selections.csv", unresolved_rows)

    acceptance_subjects = [
        "Electrical V3-P1.15 independent net review", "DXL-STAR-P0.2 independent schematic review", "DXL-STAR P0.1/P0.2 copper-geometry parity",
        "P0.3 carrier received dimensions", "backplate received dimensions", "carrier placement/no-overlap", "connector and harness sweep",
        "depth and cover closure", "mounting hardware and hole process", "protective bonding/grounding", "HAR-CIN exact endpoints and lengths",
        "HAR-COUT exact endpoints and lengths", "crimp process qualification", "100 percent continuity/polarity/isolation", "strain relief and retention",
        "source/fuse/conductor/connector coordination", "steady-state thermal", "inrush and forward-current behavior", "reverse-energy/regeneration",
        "fault injection and no-backfeed", "DXL waveform/error/EMC", "qualified electrical review", "qualified functional-safety review", "written work authorization",
    ]
    acceptance_rows = [{"acceptance_id": f"CIA-{i:03d}", "subject": subject, "required_evidence": "executed configuration-specific record with article IDs, raw data, instruments/calibration and signed disposition", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for i, subject in enumerate(acceptance_subjects, 1)]
    write_csv(ENG / "acceptance-matrix.csv", acceptance_rows)

    status = {
        "identifier": IDENTIFIER, "round": "R161", "date": "2026-08-09",
        "electrical_candidate": "V3-P1.15-CARRIER-CANDIDATE", "dxl_star_candidate": "DXL-STAR-P0.2-CARRIER-CANDIDATE",
        "carrier_candidate": "HR-V0-DXL-PROT-CARRIER-P0.3", "candidate_carriers": 3,
        "net_transition_rows": len(net_rows), "placement_rows": len(placement_rows), "mounting_hole_rows": len(hole_rows),
        "route_rows": len(route_rows), "unresolved_selections": len(unresolved_rows), "acceptance_rows": len(acceptance_rows),
        "source_hashes": {key: sha256(path) for key, path in SOURCES.items()},
        "pre_post_net_ambiguity_closed_in_candidate": True, "panel_nominal_boundary_screen_passed": True,
        "cut_lengths_selected": False, "mounting_released": False, "carrier_pcba_released": False, "dxl_star_pcba_released": False,
        "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "safety_credit": False, "warning": WARNING,
    }

    for name in ("net-transition-matrix.csv", "panel-placement-screen.csv", "mounting-hole-screen.csv", "route-bound-screen.csv", "source-register.csv", "unresolved-selections.csv", "acceptance-matrix.csv"):
        shutil.copy2(ENG / name, OUT / name)
    for directory in (ENG, OUT):
        write_text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
        write_text(directory / "README.md", f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR161 inserts three explicit P0.3 carrier candidates into a separate Electrical V3-P1.15 native source, renames DXL-STAR P0.2 to post-limiter rails, and screens three carrier placements inside P0.6 BP-026. Route distances are geometric screens, not cut lengths. Twelve selections and twenty-four physical/qualified acceptance rows remain open.\n")

    rects = (
        '<style>.reserve + text{display:none}</style>'
        + "".join(f'<g><rect x="{x}" y="{y}" width="100" height="60" class="carrier"/><text x="{x+8}" y="{y+24}">{ref}</text><text x="{x+8}" y="{y+43}" class="small">100 × 60 mm</text></g>' for ref, x, y, _ in placements)
        + '<text x="272" y="558" class="small">P0.6 reserve</text>'
    )
    net_html = "".join(f"<tr><td>{r['axis']}</td><td>{r['stage']}</td><td>{html.escape(r['reference_terminal'])}</td><td><code>{r['net']}</code></td><td>{html.escape(r['next_reference_terminal'])}</td></tr>" for r in net_rows)
    unresolved_html = "".join(f"<li><strong>{r['selection_id']}</strong><span>{html.escape(r['topic'])}</span></li>" for r in unresolved_rows)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.2rem,5vw,4.6rem);line-height:1.04;max-width:20ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.5rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:1040px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}.panel{{max-width:760px;border:3px solid var(--blue);background:#f9fdff}}.panel text{{font:700 16px Arial;fill:var(--navy)}}.panel .small{{font-size:14px}}.backplate{{fill:#eef8fc;stroke:var(--navy);stroke-width:3}}.reserve{{fill:#fff0b8;stroke:#ad7500;stroke-width:2}}.carrier{{fill:#b9e8ff;stroke:#12669f;stroke-width:3}}code,.meta,li span{{font-size:14px}}li{{margin:.8rem 0}}li strong{{display:block}}a{{color:#075a96}}</style></head><body><header><div class="meta">{IDENTIFIER} · R161 · 2026-08-09</div><h1>Every branch now has a before and an after.</h1><div class="warning">{WARNING}. Native connectivity is corrected; physical release is not.</div></header><main><p>The new candidate separates fuse output from limiter output on all three axes. The current P1.14/P0.1 baseline remains preserved while the carrier-integrated candidate is independently reviewed.</p><section class="grid"><article><b>3</b>explicit carrier blocks</article><article><b>6</b>distinct positive rails</article><article><b>24</b>open acceptance rows</article><article><b>0</b>physical articles</article></section><h2>Candidate panel placement</h2><svg class="panel" viewBox="0 0 534 686" role="img" aria-label="Nominal backplate with lower carrier placements"><rect x="1" y="1" width="531" height="683" class="backplate"/><rect x="54" y="533.4" width="323.8" height="142.4" class="reserve"/><text x="62" y="558" class="small">P0.6 BP-026 reserve</text>{rects}</svg><p>This is a boundary/no-overlap screen only. Coordinates do not authorize holes or mounting.</p><h2>Positive-rail transitions</h2><div class="table-wrap"><table><thead><tr><th>Axis</th><th>Stage</th><th>From</th><th>Net</th><th>To</th></tr></thead><tbody>{net_html}</tbody></table></div><h2>Twelve selections remain</h2><ol>{unresolved_html}</ol><p><a href="net-transition-matrix.csv">net matrix</a> · <a href="panel-placement-screen.csv">placement</a> · <a href="mounting-hole-screen.csv">hole screen</a> · <a href="route-bound-screen.csv">route bounds</a> · <a href="acceptance-matrix.csv">acceptance</a> · <a href="unresolved-selections.csv">selections</a></p></main></body></html>'''
    write_text(OUT / "index.html", page)

    for directory in (ENG, OUT):
        files = sorted(path for path in directory.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
        rows = [{"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in files]
        write_csv(directory / "file-manifest.csv", rows)

    print(f"{IDENTIFIER}: 3 carriers / 15 net transitions / 3 placements / 24 acceptance rows OPEN")
    print(WARNING)


if __name__ == "__main__":
    main()
