"""Generate the review-only DXL-STAR-P0.2 carrier-aware manufacturing evidence package.

This package is configuration and CAM review evidence only. It does not
authorize supplier contact, upload, quotation, fabrication, assembly,
connection, motion, energization, or functional-safety credit.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import shutil
import subprocess
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star-p0.2-carrier-candidate"
OUT = ROOT / "release" / "hr-v0" / "dxl-star-manufacturing-p0.2"
KICAD = Path(os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"))
IDENTIFIER = "HR-V0-DXL-STAR-MFG-P0.2"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
CONNECTOR_REFS = {"JC1", "JP1", "JP2", "JP3", "JA1", "JA2", "JA3"}
MECHANICAL_REFS = {"MH1", "MH2", "MH3", "MH4"}


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(log: list[str], *args: str) -> None:
    command = [str(KICAD), *map(str, args)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    log.extend(["$ " + subprocess.list2cmdline(command), result.stdout, result.stderr, f"exit={result.returncode}\n"])
    if result.returncode:
        raise RuntimeError(f"KiCad command failed ({result.returncode}): {command}")


def pad_net(footprint, terminal: str) -> str:
    matches = [pad for pad in footprint.Pads() if pad.GetNumber() == terminal]
    if len(matches) != 1:
        raise RuntimeError(f"expected one pad {footprint.GetReference()}.{terminal}, found {len(matches)}")
    return matches[0].GetNetname()


def main() -> None:
    if not KICAD.exists():
        raise FileNotFoundError(KICAD)
    board_path = SOURCE / "hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb"
    project_path = SOURCE / "hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pro"
    source_bom = SOURCE / "bom.csv"
    connector_schedule = SOURCE / "connector-schedule.csv"
    for path in (board_path, project_path, source_bom, connector_schedule):
        if not path.exists():
            raise FileNotFoundError(path)

    if OUT.exists():
        resolved = OUT.resolve()
        expected_parent = (ROOT / "release" / "hr-v0").resolve()
        if resolved.parent != expected_parent or resolved.name != "dxl-star-manufacturing-p0.2":
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    for directory in (OUT / "source", OUT / "cam" / "gerbers", OUT / "cam" / "drill"):
        directory.mkdir(parents=True, exist_ok=True)

    controlled_board = OUT / "source" / board_path.name
    controlled_project = OUT / "source" / project_path.name
    shutil.copy2(board_path, controlled_board)
    shutil.copy2(project_path, controlled_project)

    log: list[str] = []
    stem = "hr-v0-dxl-star-p0.2-carrier-candidate"
    run(log, "pcb", "drc", "--output", str(OUT / "cam" / f"{stem}-drc.rpt"), "--format", "report", "--units", "mm", "--severity-all", "--exit-code-violations", str(controlled_board))
    run(log, "pcb", "export", "gerbers", "--output", str(OUT / "cam" / "gerbers"), "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts", "--precision", "6", "--check-zones", str(controlled_board))
    run(log, "pcb", "export", "drill", "--output", str(OUT / "cam" / "drill"), "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "svg", "--generate-report", "--report-path", str(OUT / "cam" / "drill" / f"{stem}-drill-report.txt"), str(controlled_board))
    run(log, "pcb", "export", "pos", "--output", str(OUT / "cam" / f"{stem}-all-pos.csv"), "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp", str(controlled_board))
    run(log, "pcb", "export", "ipcd356", "--output", str(OUT / "cam" / f"{stem}.d356"), str(controlled_board))
    run(log, "pcb", "export", "stats", "--output", str(OUT / "cam" / f"{stem}-stats.json"), "--format", "json", "--units", "mm", str(controlled_board))
    write_text_lf(OUT / "cam" / "kicad-cli.log", "\n".join(log))
    (OUT / "source" / f"{stem}.kicad_prl").unlink(missing_ok=True)
    shutil.rmtree(OUT / "source")

    board = pcbnew.LoadBoard(str(board_path))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if set(footprints) != CONNECTOR_REFS | MECHANICAL_REFS:
        raise RuntimeError("native footprint membership changed")

    raw_positions = {row["Ref"]: row for row in read_csv(OUT / "cam" / f"{stem}-all-pos.csv")}
    if set(raw_positions) != CONNECTOR_REFS:
        raise RuntimeError(f"position membership changed: {sorted(raw_positions)}")
    parity_rows: list[dict[str, object]] = []
    x_offsets: set[float] = set()
    y_offsets: set[float] = set()
    max_error = 0.0
    max_rotation_error = 0.0
    for ref in sorted(CONNECTOR_REFS):
        raw = raw_positions[ref]
        footprint = footprints[ref]
        raw_x = float(raw["PosX"])
        raw_y = float(raw["PosY"])
        raw_rotation = float(raw["Rot"])
        native_x = pcbnew.ToMM(footprint.GetPosition().x)
        native_y = pcbnew.ToMM(footprint.GetPosition().y)
        native_rotation = footprint.GetOrientation().AsDegrees() % 360.0
        x_offset = round(raw_x - native_x, 6)
        y_offset = round((-raw_y) - native_y, 6)
        x_offsets.add(x_offset)
        y_offsets.add(y_offset)
        position_error = max(abs((raw_x - x_offset) - native_x), abs(((-raw_y) - y_offset) - native_y))
        rotation_error = abs(((raw_rotation - native_rotation + 180.0) % 360.0) - 180.0)
        max_error = max(max_error, position_error)
        max_rotation_error = max(max_rotation_error, rotation_error)
        parity_rows.append({
            "reference": ref,
            "kicad_pos_x_mm": f"{raw_x:.6f}",
            "kicad_pos_y_mm": f"{raw_y:.6f}",
            "kicad_rotation_deg": f"{raw_rotation:.6f}",
            "native_center_x_mm": f"{native_x:.6f}",
            "native_center_y_mm": f"{native_y:.6f}",
            "native_rotation_deg": f"{native_rotation:.6f}",
            "derived_x_offset_mm": f"{x_offset:.6f}",
            "derived_inverted_y_offset_mm": f"{y_offset:.6f}",
            "position_error_mm": f"{position_error:.9f}",
            "rotation_error_deg": f"{rotation_error:.9f}",
            "state": "PARITY PASS - INTERNAL COORDINATES ONLY - NOT MACHINE XYRS",
            "warning": WARNING,
        })
    if len(x_offsets) != 1 or len(y_offsets) != 1 or max_error > 1e-6 or max_rotation_error > 1e-6:
        raise RuntimeError(f"position parity failed: x={x_offsets} y={y_offsets} pos={max_error} rot={max_rotation_error}")
    write_csv(OUT / "placement-parity-register.csv", list(parity_rows[0]), parity_rows)
    write_text_lf(OUT / "position-transform.json", json.dumps({
        "source": "KiCad CLI raw position export",
        "comparison": "native DXL-STAR-P0.2-CARRIER-CANDIDATE footprint centers and rotations",
        "reference_count": 7,
        "derived_relation": "native_x = kicad_pos_x - x_offset; native_y = -kicad_pos_y - inverted_y_offset",
        "x_offset_mm": next(iter(x_offsets)),
        "inverted_y_offset_mm": next(iter(y_offsets)),
        "max_position_error_mm": max_error,
        "max_rotation_error_deg": max_rotation_error,
        "supplier_normalized": False,
        "machine_import_authorized": False,
        "warning": WARNING,
    }, indent=2) + "\n")

    source_bom_rows = read_csv(source_bom)
    assembly_rows = [{
        "reference": row["reference"],
        "value": row["value"],
        "quantity": row["quantity"],
        "source_status": row["status"],
        "assembly_state": "APPLICATION HOLD - NOT RELEASED",
        "warning": WARNING,
    } for row in source_bom_rows]
    write_csv(OUT / "assembly-bom-register.csv", list(assembly_rows[0]), assembly_rows)

    terminal_rows = []
    for row in read_csv(connector_schedule):
        native = pad_net(footprints[row["reference"]], row["terminal"])
        scheduled = row["net"]
        expected_native = "" if scheduled == "INTENTIONALLY_UNUSED_U2D2_VDD" else scheduled
        terminal_rows.append({
            "reference": row["reference"],
            "terminal": row["terminal"],
            "pin_name": row["pin_name"],
            "schedule_net": scheduled,
            "native_pad_net": native or "NO_NET_NO_COPPER",
            "parity": "PASS" if native == expected_native else "FAIL",
            "source_status": row["status"],
            "release_state": "APPLICATION HOLD - NOT RELEASED",
            "warning": WARNING,
        })
    if any(row["parity"] != "PASS" for row in terminal_rows):
        raise RuntimeError("terminal schedule/native board parity failed")
    write_csv(OUT / "terminal-parity-register.csv", list(terminal_rows[0]), terminal_rows)

    mechanical_rows = []
    for ref in sorted(MECHANICAL_REFS):
        fp = footprints[ref]
        pads = list(fp.Pads())
        drill = pads[0].GetDrillSize() if len(pads) == 1 else None
        mechanical_rows.append({
            "reference": ref,
            "feature": "NPTH mounting hole",
            "center_x_mm": f"{pcbnew.ToMM(fp.GetPosition().x):.3f}",
            "center_y_mm": f"{pcbnew.ToMM(fp.GetPosition().y):.3f}",
            "drill_x_mm": f"{pcbnew.ToMM(drill.x):.3f}" if drill else "",
            "drill_y_mm": f"{pcbnew.ToMM(drill.y):.3f}" if drill else "",
            "release_state": "DIMENSIONAL REVIEW REQUIRED - NOT RELEASED",
            "warning": WARNING,
        })
    write_csv(OUT / "mechanical-feature-register.csv", list(mechanical_rows[0]), mechanical_rows)

    holds = [
        ("DXL-MFG-HOLD-001", "fabricator/assembler selection", "named provider capability, terms, traceability and qualified acceptance"),
        ("DXL-MFG-HOLD-002", "material/stackup/copper/finish/mask/legend", "frozen fabrication specification and provider capability response"),
        ("DXL-MFG-HOLD-003", "holes/profile/panel/electrical test", "finished tolerances, panel/tooling definition and bare-board test plan"),
        ("DXL-MFG-HOLD-004", "independent CAM preview", "layer-by-layer copper, mask, silk, outline, PTH and NPTH review"),
        ("DXL-MFG-HOLD-005", "connector footprint/polarity", "qualified land-pattern, orientation, keying and pin-1 review"),
        ("DXL-MFG-HOLD-006", "connector sourcing and alternates", "exact orderable headers, traceable lots and approved alternates"),
        ("DXL-MFG-HOLD-007", "mating housings and contacts", "exact housing/contact/empty-cavity identities and received compatibility"),
        ("DXL-MFG-HOLD-008", "branch conductor system", "wire gauge, length, bundling, insulation and connector derating evidence"),
        ("DXL-MFG-HOLD-009", "crimp process", "tooling, strip length, crimp-height, inspection and pull-test evidence"),
        ("DXL-MFG-HOLD-010", "branch protection coordination", "selected fuse/protection values with fault current, inrush, duty and clearing evidence"),
        ("DXL-MFG-HOLD-011", "connector/actuator current conflict", "thermal/current proof resolving 3 A EH connector rating versus XM540 4.4 A stall current"),
        ("DXL-MFG-HOLD-012", "DXL signal integrity", "baud, cable topology/length, loading, waveform margin and error-rate evidence"),
        ("DXL-MFG-HOLD-013", "U2D2 no-backfeed", "power-sequence and fault tests proving omitted VDD does not backfeed"),
        ("DXL-MFG-HOLD-014", "return/PE/shield implementation", "single-point bonding, shield termination and common-mode evidence"),
        ("DXL-MFG-HOLD-015", "thermal/load validation", "representative continuous/peak load temperature rise and derating evidence"),
        ("DXL-MFG-HOLD-016", "first article and electrical acceptance", "received identity, dimensions, continuity/isolation and workmanship evidence"),
        ("DXL-MFG-HOLD-017", "HIL/fault/EMC validation", "branch-open/short, data faults, power sequencing, emissions and immunity evidence"),
        ("DXL-MFG-HOLD-018", "qualified release and work authority", "named qualified review plus separate written authority for each work stage"),
    ]
    hold_rows = [{"hold_id": i, "subject": s, "status": "OPEN", "evidence_needed": e, "warning": WARNING} for i, s, e in holds]
    write_csv(OUT / "manufacturing-release-holds.csv", list(hold_rows[0]), hold_rows)

    stats = json.loads((OUT / "cam" / f"{stem}-stats.json").read_text(encoding="utf-8"))
    inputs = [
        ("DXL-MFG-IN-001", "native board identity", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "SOURCE BOUND"),
        ("DXL-MFG-IN-002", "board outline", f"{stats['board']['width']} x {stats['board']['height']}", "SOURCE BOUND"),
        ("DXL-MFG-IN-003", "native thickness setting", stats["board"]["board_thickness"], "REVIEW INPUT - SUPPLIER TOLERANCE REQUIRED"),
        ("DXL-MFG-IN-004", "minimum routed track width", stats["board"]["min_track_width"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("DXL-MFG-IN-005", "minimum routed clearance", stats["board"]["min_track_clearance"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("DXL-MFG-IN-006", "minimum drill diameter", stats["board"]["min_drill_diameter"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("DXL-MFG-IN-007", "layer count", "2 copper layers", "SOURCE BOUND"),
        ("DXL-MFG-IN-008", "base material and Tg", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-009", "copper foil and finished copper", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-010", "surface finish", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-011", "solder mask system and color", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-012", "legend system and color", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-013", "finished holes and plating tolerances", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-014", "outline/profile tolerance", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-015", "panelization, rails, tooling and fiducials", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-016", "bare-board electrical test and coupon", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-017", "controlled impedance disposition", "SELECTION REQUIRED", "OPEN"),
        ("DXL-MFG-IN-018", "fabricator and assembler", "SELECTION REQUIRED", "OPEN"),
    ]
    input_rows = [{"input_id": i, "subject": s, "candidate_value": v, "state": t, "warning": WARNING} for i, s, v, t in inputs]
    write_csv(OUT / "manufacturing-input-register.csv", list(input_rows[0]), input_rows)

    gerber_paths = sorted(path for path in (OUT / "cam" / "gerbers").glob("*") if path.is_file())
    drill_paths = sorted(path for path in (OUT / "cam" / "drill").glob("*") if path.is_file())
    output_paths = [*gerber_paths, *drill_paths, OUT / "cam" / f"{stem}-all-pos.csv", OUT / "cam" / f"{stem}.d356", OUT / "cam" / f"{stem}-stats.json", OUT / "cam" / f"{stem}-drc.rpt"]
    output_rows = []
    for path in output_paths:
        rel = path.relative_to(OUT).as_posix()
        role = "GERBER_OR_JOB" if "/gerbers/" in f"/{rel}" else "DRILL_OR_MAP_OR_REPORT" if "/drill/" in f"/{rel}" else "IPC_D_356_REVIEW_NETLIST" if path.suffix == ".d356" else "KICAD_INTERNAL_POSITION_EXPORT_NOT_MACHINE_XYRS" if path.name.endswith("-all-pos.csv") else "NATIVE_DRC_REPORT" if path.name.endswith("-drc.rpt") else "BOARD_STATISTICS"
        output_rows.append({"path": rel, "role": role, "bytes": path.stat().st_size, "sha256": sha256(path), "release_state": "INTERNAL REVIEW ONLY - NOT RELEASED TO SUPPLIER", "warning": WARNING})
    write_csv(OUT / "cam-output-register.csv", list(output_rows[0]), output_rows)

    source_paths = [board_path, project_path, source_bom, connector_schedule]
    source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in source_paths}
    status = {
        "identifier": IDENTIFIER,
        "round": "R164",
        "date": "2026-08-09",
        "board": "DXL-STAR-P0.2-CARRIER-CANDIDATE",
        "native_tool": "KiCad 10.0.5",
        "source_hashes": source_hashes,
        "populated_references": 7,
        "connector_terminals": 18,
        "mechanical_features": 4,
        "gerber_and_job_files": len(gerber_paths),
        "drill_map_report_files": len(drill_paths),
        "position_parity_references": len(parity_rows),
        "position_parity_max_error_mm": max_error,
        "position_parity_max_rotation_error_deg": max_rotation_error,
        "terminal_parity_rows": len(terminal_rows),
        "open_holds": len(hold_rows),
        "cam_generated": True,
        "cam_review_only": True,
        "cam_released": False,
        "supplier_normalized_xyrs_exists": False,
        "supplier_selected": False,
        "supplier_contacted": False,
        "files_uploaded": False,
        "quotation_requested": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "physical_article_exists": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    write_text_lf(OUT / "package-status.json", json.dumps(status, indent=2) + "\n")

    readme = f"""# {IDENTIFIER}\n\n> **{WARNING}**\n\nThis is a source-bound CAM and assembly **review** package for native board `DXL-STAR-P0.2-CARRIER-CANDIDATE`. It is not a supplier packet and contains no machine-ready assembler XYRS.\n\n## What exists\n\n- fresh KiCad 10.0.5 DRC, Gerber/job, separate PTH/NPTH drill, IPC-D-356, raw position and statistics outputs;\n- exact SHA-256 identities for the native board/project, source BOM and connector schedule;\n- seven connector placement parity rows and eighteen terminal-to-native-pad parity rows;\n- seven proposed connector BOM rows and four mounting-hole records; and\n- eighteen manufacturing inputs, eighteen open release holds and a checksum manifest.\n\n## Boundary\n\nThe connector families remain application holds. Harness lengths, conductor gauges, fuses/protection, current/thermal limits, crimp process, signal integrity, no-backfeed, grounding/shielding, physical validation, supplier/process, DFM, first article and qualified release remain unresolved. The raw position export is not supplier-normalized XYRS. No archive or upload bundle is produced.\n\nPassing the checker proves only source/output membership, hashes, native DRC and encoded parity. It does not prove manufacturability, electrical performance, safety, or permission to perform work.\n"""
    write_text_lf(OUT / "README.md", readme)

    cards = [("7", "connector footprints in placement parity"), ("18", "terminal mappings checked against native pads"), (str(len(gerber_paths)), "Gerber and job files for internal review"), ("0", "supplier releases or work authorizations")]
    card_html = "".join(f"<article><b>{value}</b><span>{html.escape(label)}</span></article>" for value, label in cards)
    hold_html = "".join(f"<li><strong>{i}</strong> {html.escape(s)}<br><span>{html.escape(e)}</span></li>" for i, s, e in holds)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif;background:white}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.3rem,5.5vw,4.8rem);line-height:1.03;max-width:18ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.7rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}article span{{display:block}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:980px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code{{font-size:14px;overflow-wrap:anywhere}}li{{margin:.8rem 0}}li span{{font-size:14px}}a{{color:#075d98}}</style></head><body><header><div>{IDENTIFIER} &middot; R164 &middot; 2026-08-09</div><h1>DXL-STAR-P0.2-CARRIER-CANDIDATE CAM exists for review.</h1><div class="warning">{WARNING}. The files are quarantined internal evidence, not a supplier packet.</div></header><main><p>KiCad 10.0.5 generated a fresh CAM review set from the controlled DYNAMIXEL star board. This closes the absence of current output evidence only.</p><section class="grid">{card_html}</section><div class="boundary"><h2>What the board encodes</h2><p>Three positive actuator branches remain isolated. The DXL data and actuator return nets are common. JC1 pin 2 is deliberately empty and carries no VDD copper. Those facts are encoded parity&mdash;not physical validation.</p></div><h2>Controlled review files</h2><div class="table-wrap"><table><thead><tr><th>Artifact</th><th>State</th><th>Use</th></tr></thead><tbody><tr><td><code>cam/gerbers/</code></td><td>{len(gerber_paths)} files</td><td>INTERNAL LAYER PREVIEW ONLY</td></tr><tr><td><code>cam/drill/</code></td><td>{len(drill_paths)} files</td><td>INTERNAL DRILL PREVIEW ONLY</td></tr><tr><td><code>cam/{stem}-all-pos.csv</code></td><td>7 references</td><td>NOT MACHINE XYRS</td></tr><tr><td><code>terminal-parity-register.csv</code></td><td>18 terminals</td><td>ENCODED PARITY ONLY</td></tr><tr><td><code>manufacturing-input-register.csv</code></td><td>18 inputs</td><td>11 SELECTION REQUIRED</td></tr></tbody></table></div><div class="boundary"><h2>Eighteen holds remain open</h2><ol>{hold_html}</ol></div><p><a href="cam-output-register.csv">CAM register</a> &middot; <a href="terminal-parity-register.csv">terminal parity</a> &middot; <a href="manufacturing-release-holds.csv">release holds</a></p></main></body></html>'''
    # Use ASCII HTML entities for punctuation so basic local HTTP servers cannot
    # misdecode UTF-8 punctuation in this review guide.
    page = (
        page.replace("\u00c2\u00b7", "&middot;")
        .replace("\u00e2\u20ac\u201d", "&mdash;")
        .replace("\u00b7", "&middot;")
        .replace("\u2014", "&mdash;")
    )
    write_text_lf(OUT / "index.html", page)

    manifest_rows = [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")]
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256"], manifest_rows)
    print(f"{IDENTIFIER}: {len(gerber_paths)} Gerber/job + {len(drill_paths)} drill/map/report files; 7 placements; 18 terminals; 18 holds OPEN")
    print(WARNING)


if __name__ == "__main__":
    main()
