"""Generate the controlled HR-V0 watchdog PCB CAM candidate.

This package is review evidence only. It never authorizes portal upload,
fabrication, assembly, energization, or safety credit.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3"
OUT = ROOT / "release" / "hr-v0" / "watchdog-pcb-fabrication-candidate-p0.1"
KICAD = Path(os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"))
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
IDENTIFIER = "HR-V0-WD-FAB-P0.1"
BOARD_REFS = {
    "CDEC1", "CDRV1", "CDRV2", "CFI1", "CFI2", "DC1", "ISO1", "JWF1", "JWH1", "JWP1",
    "RHB1", "RHP1", "RPD1", "RPD2", "RSN1", "RSN2", "RSO1", "RSO2", "RTH1", "RTH2",
    "RW1", "RW2", "UDRV1", "UDRV2", "UFB1", "WDCTRL1",
    *{f"TP{i}" for i in range(1, 17)},
}


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(log: list[str], *args: str) -> None:
    command = [str(KICAD), *map(str, args)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    log.extend(["$ " + subprocess.list2cmdline(command), result.stdout, result.stderr, f"exit={result.returncode}\n"])
    if result.returncode:
        raise RuntimeError(f"KiCad command failed ({result.returncode}): {command}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not KICAD.exists():
        raise FileNotFoundError(KICAD)
    if OUT.exists():
        shutil.rmtree(OUT)
    for directory in (OUT / "source", OUT / "cam" / "gerbers", OUT / "cam" / "drill"):
        directory.mkdir(parents=True, exist_ok=True)

    board = SOURCE / "project-button-v3.kicad_pcb"
    project = SOURCE / "project-button-v3.kicad_pro"
    controlled_board = OUT / "source" / board.name
    controlled_project = OUT / "source" / project.name
    shutil.copy2(board, controlled_board)
    shutil.copy2(project, controlled_project)

    log: list[str] = []
    run(log, "pcb", "drc", "--output", str(OUT / "cam" / "project-button-v3-drc.rpt"),
        "--format", "report", "--units", "mm", "--severity-all", "--exit-code-violations", str(controlled_board))
    run(log, "pcb", "export", "gerbers", "--output", str(OUT / "cam" / "gerbers"),
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
        "--precision", "6", "--check-zones", str(controlled_board))
    run(log, "pcb", "export", "drill", "--output", str(OUT / "cam" / "drill"),
        "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th",
        "--generate-map", "--map-format", "svg", "--generate-report",
        "--report-path", str(OUT / "cam" / "drill" / "project-button-v3-drill-report.txt"), str(controlled_board))
    run(log, "pcb", "export", "pos", "--output", str(OUT / "cam" / "project-button-v3-all-pos.csv"),
        "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp", str(controlled_board))
    run(log, "pcb", "export", "ipcd356", "--output", str(OUT / "cam" / "project-button-v3.d356"), str(controlled_board))
    run(log, "pcb", "export", "stats", "--output", str(OUT / "cam" / "project-button-v3-stats.json"),
        "--format", "json", "--units", "mm", str(controlled_board))
    (OUT / "cam" / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
    # KiCad may create per-user UI state next to the controlled project while
    # invoking the CLI. It is not design source and must not enter the package.
    (OUT / "source" / "project-button-v3.kicad_prl").unlink(missing_ok=True)

    with (SOURCE / "bom.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    by_ref = {row["reference"]: row for row in source_rows if row["reference"] in BOARD_REFS}
    missing = BOARD_REFS - by_ref.keys()
    if missing:
        raise RuntimeError(f"board BOM rows missing: {sorted(missing)}")
    grouped: dict[tuple[str, str, str, str], list[str]] = {}
    for ref, row in by_ref.items():
        key = (row["value"], row["status"], row["datasheet"], row["evidence"])
        grouped.setdefault(key, []).append(ref)
    bom_rows = []
    for (value, status, datasheet, evidence), refs in sorted(grouped.items(), key=lambda item: sorted(item[1])[0]):
        bom_rows.append({"references": " ".join(sorted(refs)), "quantity": len(refs), "candidate_part": value,
                         "status": status, "datasheet": datasheet, "evidence": evidence,
                         "release_state": "NOT RELEASED"})
    write_csv(OUT / "assembly-bom.csv",
              ["references", "quantity", "candidate_part", "status", "datasheet", "evidence", "release_state"], bom_rows)

    parameters = [
        ("copper_layers", "2", "PROPOSED"), ("finished_thickness", "1.6 mm nominal", "PROPOSED"),
        ("copper_weight", "1 oz each side", "PROPOSED"), ("material", "175 Tg FR-4; UL94 V-0", "PROPOSED"),
        ("finish", "ENIG", "PROPOSED"), ("solder_mask", "Purple SMOBC", "PROPOSED"),
        ("minimum_trace_space", "0.1524 mm / 0.1524 mm", "SOURCE CHECKED"),
        ("minimum_drill", "0.254 mm supplier minimum; design minimum 0.300 mm", "SOURCE CHECKED"),
        ("minimum_annular_ring", "0.127 mm supplier minimum; design minimum 0.150 mm", "SOURCE CHECKED"),
        ("board_outline", "160 mm x 100 mm", "SOURCE CHECKED"),
        ("supplier", "OSH Park Two Layer Prototype Service candidate", "SELECTION REQUIRED"),
        ("native_file_compatibility", "Supplier documents latest stable direct KiCad processing as 9.x; use reviewed Gerbers for this KiCad 10.0.5 source", "HOLD"),
    ]
    write_csv(OUT / "fabrication-parameters.csv", ["parameter", "candidate_value", "status", "source", "accessed"],
              [{"parameter": p, "candidate_value": v, "status": s,
                "source": "https://docs.oshpark.com/services/two-layer/", "accessed": "2026-08-08"} for p, v, s in parameters])

    hold_texts = [
        "Independent schematic-to-PCB parity and layout review", "Official land-pattern, paste, mask, polarity and orientation review",
        "Independent CAM preview of every copper, mask, silkscreen, outline and drill layer", "Supplier portal preview and written acceptance of the controlled archive",
        "KiCad 10 source compatibility disposition; Gerber archive is mandatory for candidate submission", "Exact-part availability and written alternate-part control",
        "Fault-current, foldback, protection, connector and trace coordination", "Assembly process, ESD, cleanliness and rework controls",
        "Bare-board continuity, isolation and dimensional inspection", "Assembled-board receiving inspection and AOI/manual inspection",
        "Current-limited staged bring-up with no safety or actuator source connected", "HIL, fault injection, brownout, thermal and EMC/surge evidence",
        "Enclosure, mounting, harness, strain relief, segregation and service-access definition", "Qualified electrical and functional-safety review and written authorization",
    ]
    write_csv(OUT / "fabrication-holds.csv", ["hold_id", "hold", "state", "closure_evidence"],
              [{"hold_id": f"WD-FAB-HOLD-{i:02d}", "hold": text, "state": "OPEN", "closure_evidence": "NONE"}
               for i, text in enumerate(hold_texts, 1)])
    write_csv(OUT / "source-register.csv", ["source_id", "organization", "document", "revision_or_date", "url", "accessed", "use"], [
        {"source_id": "SRC-001", "organization": "OSH Park", "document": "2 Layer Prototype Service", "revision_or_date": "No revision stated", "url": "https://docs.oshpark.com/services/two-layer/", "accessed": "2026-08-08", "use": "Candidate process envelope"},
        {"source_id": "SRC-002", "organization": "OSH Park", "document": "KiCad support", "revision_or_date": "No revision stated; page identifies KiCad 9.x", "url": "https://docs.oshpark.com/design-tools/kicad/", "accessed": "2026-08-08", "use": "Native-version compatibility hold"},
        {"source_id": "SRC-003", "organization": "OSH Park", "document": "Generating KiCad Gerbers", "revision_or_date": "No revision stated", "url": "https://docs.oshpark.com/design-tools/kicad/generating-kicad-gerbers/", "accessed": "2026-08-08", "use": "CAM layer set"},
    ])

    status = {
        "identifier": IDENTIFIER, "date": str(date.today()), "warning": WARNING,
        "board_revision": "PCB-P0.5", "electrical_compatibility": "Project Button Electrical V3-P1.13",
        "native_tool": "KiCad 10.0.5", "board_component_references": len(BOARD_REFS),
        "cam_generated": True, "cam_released": False, "supplier_selected": False,
        "portal_upload_authorized": False, "fabrication_order_authorized": False,
        "assembly_authorized": False, "energization_authorized": False, "safety_credit": False,
        "open_holds": len(hold_texts),
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = f"""# {IDENTIFIER}\n\n> **{WARNING}**\n\nThis is a deterministic **CAM review candidate** for watchdog PCB `PCB-P0.5`, compatible with Electrical V3-P1.13. It is not a manufacturing release. Do not upload it to a supplier portal, order it, assemble it, connect it to a safety circuit, or energize it.\n\n## What is present\n\n- an immutable copy of the KiCad 10.0.5 board/project source;\n- fresh DRC, Gerber, PTH/NPTH drill, position, IPC-D-356 and board-statistics outputs;\n- a 42-reference candidate assembly BOM;\n- the proposed fabrication envelope, primary-source register and 14 open holds; and\n- checksums for every controlled file.\n\nThe native source includes four additional mechanical mounting-hole footprints. Native KiCad DRC must remain zero. Generated CAM is evidence for independent review only.\n\n## Compatibility decision\n\nOSH Park's current KiCad page documents direct processing using KiCad 9.x, while this source is KiCad 10.0.5. Therefore direct native-file submission is not assumed compatible. A qualified reviewer must inspect the generated Gerbers and supplier preview before any later, separately authorized fabrication release.\n\n## Release state\n\nAll authorization flags in `package-status.json` are false. Every row in `fabrication-holds.csv` is open. Passing the package checker proves deterministic source/output consistency, not physical correctness or safety.\n"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    cards = "".join(f"<li><strong>{html.escape(r['hold_id'])}</strong> {html.escape(r['hold'])}</li>" for r in
                    [{"hold_id": f"WD-FAB-HOLD-{i:02d}", "hold": text} for i, text in enumerate(hold_texts, 1)])
    page = f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>{IDENTIFIER}</title><style>:root{{--sky:#dff3ff;--blue:#0a2e5c;--gold:#f3ba21;--paper:#fffdf7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--blue);font:16px/1.55 system-ui,sans-serif}}header,main{{max-width:1100px;margin:auto;padding:28px}}header{{background:var(--blue);color:white;max-width:none}}header div{{max-width:1100px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4rem);margin:.2rem 0}}.warning{{background:var(--gold);color:#18233b;font-weight:800;padding:16px;border:3px solid #18233b}}section{{background:var(--paper);padding:24px;margin:24px 0;border:2px solid var(--blue);border-radius:14px}}li{{margin:.7rem 0}}code{{font-size:1rem}}a{{color:#064d91}}.no{{font-size:1.25rem;font-weight:800}}</style>
<header><div><p>{IDENTIFIER}</p><h1>Watchdog PCB CAM review candidate</h1><p>{WARNING}</p></div></header><main><p class=warning>No supplier upload. No order. No assembly. No energization. No safety credit.</p><section><h2>What this proves</h2><p>The controlled KiCad source generated a fresh zero-violation DRC and a deterministic review set containing Gerbers, drill data, placement data, an IPC-D-356 netlist, board statistics and a 42-reference candidate BOM.</p><p>It does not prove footprint correctness, supplier acceptance, assembly quality, electrical performance, fault tolerance or functional safety.</p></section><section><h2>Fourteen open release holds</h2><ol>{cards}</ol></section><section><h2>Next controlled action</h2><p class=no>Independent CAM and footprint review only.</p><p>Use <code>fabrication-holds.csv</code>, <code>fabrication-parameters.csv</code>, and the files in <code>cam/</code>. Record evidence; do not edit a hold to closed without a traceable reviewer and artifact.</p></section></main></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")

    rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256"], rows)
    print(f"Generated {IDENTIFIER}: {len(rows)} controlled files; {len(hold_texts)} holds OPEN")


if __name__ == "__main__":
    main()
