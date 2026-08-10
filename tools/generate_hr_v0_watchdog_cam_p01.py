"""Generate a source-bound watchdog PCB CAM review package.

The package is review evidence only. It never authorizes supplier contact,
upload, quotation, fabrication, assembly, connection, motion, energization,
or functional-safety credit.
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


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3"
P115_SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"
P115_PARITY = ROOT / "release" / "hr-v0" / "e2-p115-parity-p0.1"
ASSEMBLY = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
KICAD = Path(os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"))
PROFILE = os.environ.get("HR_V0_WD_CAM_PROFILE", "p0.1")
if PROFILE not in {"p0.1", "p0.2"}:
    raise ValueError(f"unsupported watchdog CAM profile: {PROFILE}")
CURRENT_P115 = PROFILE == "p0.2"
OUT = ROOT / "release" / "hr-v0" / f"watchdog-pcb-cam-{PROFILE}"
IDENTIFIER = f"HR-V0-WD-CAM-{PROFILE.upper()}"
ROUND = "R195" if CURRENT_P115 else "R150"
BOARD_BINDING = (
    "PCB-P1.0 / Electrical V3-P1.15-CARRIER-CANDIDATE (DIRECT NATIVE BINDING)"
    if CURRENT_P115
    else "PCB-P0.9 / Electrical V3-P1.14"
)
TITLE_TOKEN = "Direct-bound P1.15 PCB-P1.0 CAM exists for review" if CURRENT_P115 else "Current PCB-P0.9 CAM exists for review"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
BOARD_REFS = {
    "CDEC1", "CDRV1", "CDRV2", "CFI1", "CFI2", "DC1", "ISO1", "JWF1", "JWH1", "JWP1",
    "RHB1", "RHP1", "RPD1", "RPD2", "RSN1", "RSN2", "RSO1", "RSO2", "RTH1", "RTH2",
    "RW1", "RW2", "UDRV1", "UDRV2", "UFB1", "WDCTRL1", *{f"TP{i}" for i in range(1, 17)},
}


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


def main() -> None:
    if not KICAD.exists():
        raise FileNotFoundError(KICAD)
    board = SOURCE / "project-button-v3.kicad_pcb"
    project = SOURCE / "project-button-v3.kicad_pro"
    required_assembly = [
        "board-assembly-bom.csv",
        "assembly-placement-reference.csv",
        "mechanical-feature-register.csv",
        "assembly-data-holds.csv",
    ]
    for path in [board, project, *(ASSEMBLY / name for name in required_assembly)]:
        if not path.exists():
            raise FileNotFoundError(path)

    if OUT.exists():
        resolved = OUT.resolve()
        expected_parent = (ROOT / "release" / "hr-v0").resolve()
        if resolved.parent != expected_parent or resolved.name != f"watchdog-pcb-cam-{PROFILE}":
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    for directory in (OUT / "source", OUT / "cam" / "gerbers", OUT / "cam" / "drill"):
        directory.mkdir(parents=True, exist_ok=True)

    controlled_board = OUT / "source" / board.name
    controlled_project = OUT / "source" / project.name
    shutil.copy2(board, controlled_board)
    shutil.copy2(project, controlled_project)

    log: list[str] = []
    run(
        log,
        "pcb", "drc", "--output", str(OUT / "cam" / "project-button-v3-drc.rpt"),
        "--format", "report", "--units", "mm", "--severity-all", "--exit-code-violations", str(controlled_board),
    )
    run(
        log,
        "pcb", "export", "gerbers", "--output", str(OUT / "cam" / "gerbers"),
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
        "--precision", "6", "--check-zones", str(controlled_board),
    )
    run(
        log,
        "pcb", "export", "drill", "--output", str(OUT / "cam" / "drill"),
        "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th",
        "--generate-map", "--map-format", "svg", "--generate-report",
        "--report-path", str(OUT / "cam" / "drill" / "project-button-v3-drill-report.txt"), str(controlled_board),
    )
    run(
        log,
        "pcb", "export", "pos", "--output", str(OUT / "cam" / "project-button-v3-all-pos.csv"),
        "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp", str(controlled_board),
    )
    run(log, "pcb", "export", "ipcd356", "--output", str(OUT / "cam" / "project-button-v3.d356"), str(controlled_board))
    run(
        log,
        "pcb", "export", "stats", "--output", str(OUT / "cam" / "project-button-v3-stats.json"),
        "--format", "json", "--units", "mm", str(controlled_board),
    )
    write_text_lf(OUT / "cam" / "kicad-cli.log", "\n".join(log))
    (OUT / "source" / "project-button-v3.kicad_prl").unlink(missing_ok=True)
    shutil.rmtree(OUT / "source")

    raw_positions = {row["Ref"]: row for row in read_csv(OUT / "cam" / "project-button-v3-all-pos.csv")}
    assembly_positions = {
        row["reference"]: row for row in read_csv(ASSEMBLY / "assembly-placement-reference.csv")
    }
    if set(raw_positions) != BOARD_REFS or set(assembly_positions) != BOARD_REFS:
        raise RuntimeError("position membership is not the controlled 42-reference set")
    parity_rows: list[dict[str, object]] = []
    x_offsets: set[float] = set()
    y_offsets: set[float] = set()
    max_error = 0.0
    max_rotation_error = 0.0
    for ref in sorted(BOARD_REFS):
        raw = raw_positions[ref]
        assembly = assembly_positions[ref]
        raw_x = float(raw["PosX"])
        raw_y = float(raw["PosY"])
        board_x = float(assembly["board_x_mm"])
        board_y = float(assembly["board_y_mm"])
        raw_rot = float(raw["Rot"])
        assembly_rot = float(assembly["source_rotation_deg"])
        x_offset = round(raw_x - board_x, 6)
        y_offset = round((-raw_y) - board_y, 6)
        x_offsets.add(x_offset)
        y_offsets.add(y_offset)
        x_error = abs((raw_x - x_offset) - board_x)
        y_error = abs(((-raw_y) - y_offset) - board_y)
        rotation_error = abs(raw_rot - assembly_rot)
        max_error = max(max_error, x_error, y_error)
        max_rotation_error = max(max_rotation_error, rotation_error)
        parity_rows.append(
            {
                "reference": ref,
                "kicad_pos_x_mm": f"{raw_x:.6f}",
                "kicad_pos_y_mm": f"{raw_y:.6f}",
                "kicad_rotation_deg": f"{raw_rot:.6f}",
                "assembly_board_x_mm": f"{board_x:.3f}",
                "assembly_board_y_mm": f"{board_y:.3f}",
                "assembly_rotation_deg": f"{assembly_rot:.3f}",
                "derived_x_offset_mm": f"{x_offset:.6f}",
                "derived_inverted_y_offset_mm": f"{y_offset:.6f}",
                "position_error_mm": f"{max(x_error, y_error):.9f}",
                "rotation_error_deg": f"{rotation_error:.9f}",
                "state": "PARITY PASS - INTERNAL COORDINATES ONLY - NOT MACHINE XYRS",
                "warning": WARNING,
            }
        )
    if len(x_offsets) != 1 or len(y_offsets) != 1 or max_error > 1e-6 or max_rotation_error > 1e-6:
        raise RuntimeError(
            f"position transform is not exact: x={sorted(x_offsets)} y={sorted(y_offsets)} "
            f"position_error={max_error} rotation_error={max_rotation_error}"
        )
    write_csv(
        OUT / "cam-assembly-parity.csv",
        [
            "reference", "kicad_pos_x_mm", "kicad_pos_y_mm", "kicad_rotation_deg",
            "assembly_board_x_mm", "assembly_board_y_mm", "assembly_rotation_deg",
            "derived_x_offset_mm", "derived_inverted_y_offset_mm", "position_error_mm",
            "rotation_error_deg", "state", "warning",
        ],
        parity_rows,
    )
    transform = {
        "source": "KiCad CLI raw position export",
        "comparison": "HR-V0-WD-PCBA-DATA-P0.2 internal placement reference",
        "reference_count": 42,
        "derived_relation": "board_x = kicad_pos_x - x_offset; board_y = -kicad_pos_y - inverted_y_offset",
        "x_offset_mm": next(iter(x_offsets)),
        "inverted_y_offset_mm": next(iter(y_offsets)),
        "max_position_error_mm": max_error,
        "max_rotation_error_deg": max_rotation_error,
        "supplier_normalized": False,
        "machine_import_authorized": False,
        "warning": WARNING,
    }
    write_text_lf(OUT / "position-transform.json", json.dumps(transform, indent=2) + "\n")

    inherited_holds = read_csv(ASSEMBLY / "assembly-data-holds.csv")
    hold_rows = [
        {
            "hold_id": row["hold_id"],
            "subject": row["subject"],
            "status": "OPEN",
            "evidence_needed": row["evidence_needed"],
            "origin": "HR-V0-WD-PCBA-DATA-P0.2",
            "warning": WARNING,
        }
        for row in inherited_holds
    ]
    added_holds = [
        ("WD-CAM-HOLD-013", "independent CAM preview", "layer-by-layer copper, paste, mask, silk, outline, PTH and NPTH disposition"),
        ("WD-CAM-HOLD-014", "fabricator capability and process", "selected provider response covering stackup, materials, copper, finish, tolerances and electrical test"),
        ("WD-CAM-HOLD-015", "returned DFM and CAM transform", "provider-generated preview/redlines and written disposition against this source hash"),
        ("WD-CAM-HOLD-016", "supplier-normalized XYRS", "assembler origin, axes, side, centroid and rotation convention plus returned transformed 42-reference file"),
        ("WD-CAM-HOLD-017", "bare-board and first-article acceptance", "received identity, dimensions, continuity/isolation, cleanliness, inspection and controlled bring-up evidence"),
        ("WD-CAM-HOLD-018", "qualified manufacturing release", "named qualified electrical/manufacturing reviewers and separate written upload/quotation/fabrication/assembly authority"),
    ]
    hold_rows.extend(
        {
            "hold_id": hold_id,
            "subject": subject,
            "status": "OPEN",
            "evidence_needed": evidence,
            "origin": IDENTIFIER,
            "warning": WARNING,
        }
        for hold_id, subject, evidence in added_holds
    )
    write_csv(
        OUT / "cam-release-holds.csv",
        ["hold_id", "subject", "status", "evidence_needed", "origin", "warning"],
        hold_rows,
    )

    stats = json.loads((OUT / "cam" / "project-button-v3-stats.json").read_text(encoding="utf-8"))
    inputs = [
        ("WD-MFG-IN-001", "native board identity", BOARD_BINDING, "SOURCE BOUND"),
        ("WD-MFG-IN-002", "board outline", f"{stats['board']['width']} x {stats['board']['height']}", "SOURCE BOUND"),
        ("WD-MFG-IN-003", "native thickness setting", stats["board"]["board_thickness"], "REVIEW INPUT - SUPPLIER TOLERANCE REQUIRED"),
        ("WD-MFG-IN-004", "minimum routed track width", stats["board"]["min_track_width"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("WD-MFG-IN-005", "minimum routed clearance", stats["board"]["min_track_clearance"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("WD-MFG-IN-006", "minimum drill diameter", stats["board"]["min_drill_diameter"], "SOURCE BOUND - CAPABILITY ACCEPTANCE REQUIRED"),
        ("WD-MFG-IN-007", "layer count", "2 copper layers", "SOURCE BOUND"),
        ("WD-MFG-IN-008", "base material and Tg", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-009", "copper foil and finished copper", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-010", "surface finish", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-011", "solder mask system and color", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-012", "legend system and color", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-013", "finished holes and plating tolerances", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-014", "outline/profile tolerance", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-015", "panelization, rails, tooling and fiducials", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-016", "bare-board electrical test and coupon", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-017", "controlled impedance requirement/disposition", "SELECTION REQUIRED", "OPEN"),
        ("WD-MFG-IN-018", "fabricator and assembly provider", "SELECTION REQUIRED", "OPEN"),
    ]
    write_csv(
        OUT / "manufacturing-input-register.csv",
        ["input_id", "subject", "candidate_value", "state", "warning"],
        [
            {"input_id": input_id, "subject": subject, "candidate_value": value, "state": state, "warning": WARNING}
            for input_id, subject, value, state in inputs
        ],
    )

    # KiCad's drill-map SVG exporter emits trailing spaces on many lines. They
    # are semantically irrelevant but make a newly added controlled package
    # fail the repository whitespace check, so normalize only those text maps
    # before computing output hashes.
    for svg_path in sorted((OUT / "cam" / "drill").glob("*.svg")):
        svg_text = svg_path.read_text(encoding="utf-8")
        svg_path.write_text(
            "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
            encoding="utf-8",
        )

    gerber_paths = sorted((OUT / "cam" / "gerbers").glob("*"))
    drill_paths = sorted((OUT / "cam" / "drill").glob("*"))
    output_paths = [
        *(path for path in gerber_paths if path.is_file()),
        *(path for path in drill_paths if path.is_file()),
        OUT / "cam" / "project-button-v3-all-pos.csv",
        OUT / "cam" / "project-button-v3.d356",
        OUT / "cam" / "project-button-v3-stats.json",
        OUT / "cam" / "project-button-v3-drc.rpt",
    ]
    output_rows = []
    for path in output_paths:
        rel = path.relative_to(OUT).as_posix()
        if "/gerbers/" in f"/{rel}":
            role = "GERBER_OR_JOB"
        elif "/drill/" in f"/{rel}":
            role = "DRILL_OR_MAP_OR_REPORT"
        elif path.suffix.lower() == ".d356":
            role = "IPC_D_356_REVIEW_NETLIST"
        elif path.name.endswith("-all-pos.csv"):
            role = "KICAD_INTERNAL_POSITION_EXPORT_NOT_MACHINE_XYRS"
        elif path.name.endswith("-drc.rpt"):
            role = "NATIVE_DRC_REPORT"
        else:
            role = "BOARD_STATISTICS"
        output_rows.append(
            {
                "path": rel,
                "role": role,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "release_state": "INTERNAL REVIEW ONLY - NOT RELEASED TO SUPPLIER",
                "warning": WARNING,
            }
        )
    write_csv(
        OUT / "cam-output-register.csv",
        ["path", "role", "bytes", "sha256", "release_state", "warning"],
        output_rows,
    )

    source_paths = [
        board,
        project,
        *(ASSEMBLY / name for name in required_assembly),
    ]
    if CURRENT_P115:
        source_paths.extend(
            [
                P115_SOURCE / "project-button-v3-p1.15-carrier-candidate.kicad_pro",
                P115_SOURCE / "project-button-v3-p1.15-carrier-candidate.kicad_sch",
                P115_SOURCE / "SOURCE-MANIFEST.csv",
            ]
        )
        for path in source_paths:
            if not path.exists():
                raise FileNotFoundError(path)
    source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in source_paths}
    status = {
        "identifier": IDENTIFIER,
        "round": ROUND,
        "date": "2026-08-10" if CURRENT_P115 else "2026-08-09",
        "board": BOARD_BINDING,
        "native_board_title_revision": "PCB-P1.0 / Electrical V3-P1.15" if CURRENT_P115 else "PCB-P0.9 / Electrical V3-P1.14",
        "current_electrical_baseline": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE" if CURRENT_P115 else "Project Button Electrical V3-P1.14",
        "p115_parity_evidence": None,
        "direct_p115_binding": CURRENT_P115,
        "assembly_data": "HR-V0-WD-PCBA-DATA-P0.2",
        "native_tool": "KiCad 10.0.5",
        "source_hashes": source_hashes,
        "populated_references": 42,
        "mechanical_features": 4,
        "gerber_and_job_files": len(gerber_paths),
        "drill_map_report_files": len(drill_paths),
        "position_parity_references": len(parity_rows),
        "position_parity_max_error_mm": max_error,
        "position_parity_max_rotation_error_deg": max_rotation_error,
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

    parity_text = (
        " The package directly binds the PCB-P1.0 native title to Electrical V3-P1.15 and hash-binds the complete P1.15 native source manifest."
        if CURRENT_P115
        else ""
    )
    readme = f"""# {IDENTIFIER}\n\n> **{WARNING}**\n\nThis is a source-bound CAM **review** package for `{BOARD_BINDING}`. It contains no supplier release and no machine-ready assembler XYRS.{parity_text}\n\n## What exists\n\n- current native KiCad board/project copies and their hashes;\n- fresh KiCad 10.0.5 DRC, Gerber/job, separate PTH/NPTH drill, IPC-D-356, raw position and statistics outputs;\n- exact source hashes for the P0.2 assembly BOM, internal placement reference, mechanical-feature register and twelve open assembly holds;\n- a 42-reference exact internal-coordinate parity proof between the raw KiCad position export and P0.2 placement reference;\n- eighteen manufacturing inputs and eighteen open release holds; and\n- a checksum manifest for every package file.\n\n## Boundary\n\nThe raw KiCad position export is not supplier-normalized XYRS and is prohibited from machine import. Material, stackup, copper, finish, mask, legend, hole/profile tolerances, panelization, electrical test, provider/process, DFM, first article, physical tests and qualified release remain unresolved. No archive or upload bundle is produced.\n\nPassing the checker proves only source/output membership, hashes, native DRC and internal coordinate parity. It does not prove manufacturability, physical correctness, electrical performance, functional safety or permission to perform work.\n"""
    write_text_lf(OUT / "README.md", readme)

    hold_items = "".join(
        f"<li><strong>{html.escape(row['hold_id'])}</strong> {html.escape(row['subject'])}<br><span>{html.escape(row['evidence_needed'])}</span></li>"
        for row in hold_rows
    )
    cards = [
        ("42", "populated references in exact coordinate parity"),
        (str(len(gerber_paths)), "Gerber and job files for internal review"),
        (str(len(drill_paths)), "drill, map and report files for internal review"),
        ("0", "supplier releases or work authorizations"),
    ]
    card_html = "".join(f"<article><b>{value}</b><span>{html.escape(label)}</span></article>" for value, label in cards)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif;background:white;overflow-wrap:anywhere}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.3rem,5.5vw,4.8rem);line-height:1.03;max-width:17ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.7rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{max-width:100%;background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article{{min-width:0;border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}article span{{display:block}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{max-width:100%;overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:980px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code{{font-size:14px;overflow-wrap:anywhere}}li{{margin:.8rem 0}}li span{{font-size:14px}}a{{color:#075d98}}@media(max-width:480px){{header{{padding:1.5rem 1.25rem}}main{{padding:1.5rem 1.25rem 3rem}}h1{{font-size:clamp(2rem,10vw,2.6rem)}}.warning{{font-size:16px}}}}</style></head><body><header><div>{IDENTIFIER} · {ROUND} · 2026-08-09</div><h1>{TITLE_TOKEN}.</h1><div class="warning">{WARNING}. The files are quarantined internal evidence, not a supplier packet.</div></header><main><p>KiCad 10.0.5 generated a fresh, source-bound CAM review set from PCB-P0.9.{parity_text} This removes the active-baseline output mismatch; it does not release the outputs.</p><section class="grid">{card_html}</section><div class="boundary"><h2>Exact internal parity, not machine XYRS</h2><p>All 42 populated references reconcile exactly between the raw KiCad position export and the P0.2 internal placement register after one derived coordinate transform. Supplier origin, axes, side, centroid, feeder and rotation conventions remain unresolved. Machine import is prohibited.</p></div><h2>Controlled package</h2><div class="table-wrap"><table><thead><tr><th>Artifact</th><th>State</th><th>Use</th></tr></thead><tbody><tr><td><code>cam/gerbers/</code></td><td>{len(gerber_paths)} files</td><td>INTERNAL LAYER PREVIEW ONLY</td></tr><tr><td><code>cam/drill/</code></td><td>{len(drill_paths)} files</td><td>INTERNAL DRILL PREVIEW ONLY</td></tr><tr><td><code>cam/project-button-v3-all-pos.csv</code></td><td>42 references</td><td>NOT MACHINE XYRS</td></tr><tr><td><code>cam/project-button-v3.d356</code></td><td>generated</td><td>INTERNAL NET REVIEW ONLY</td></tr><tr><td><code>manufacturing-input-register.csv</code></td><td>18 inputs</td><td>OPEN SELECTIONS RETAINED</td></tr></tbody></table></div><div class="boundary"><h2>Eighteen holds remain open</h2><ol>{hold_items}</ol></div><p><a href="cam-output-register.csv">CAM output register</a> · <a href="cam-assembly-parity.csv">42-reference parity</a> · <a href="manufacturing-input-register.csv">manufacturing inputs</a></p></main></body></html>'''
    if CURRENT_P115:
        page = page.replace("2026-08-09", "2026-08-10")
        page = page.replace("from PCB-P0.9.", "from PCB-P1.0.")
    write_text_lf(OUT / "index.html", page)

    manifest_rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        manifest_rows.append(
            {"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
        )
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256"], manifest_rows)
    print(
        f"{IDENTIFIER}: {len(gerber_paths)} Gerber/job + {len(drill_paths)} drill/map/report files; "
        f"42 position parity rows; {len(hold_rows)} holds OPEN"
    )
    print(WARNING)


if __name__ == "__main__":
    main()
