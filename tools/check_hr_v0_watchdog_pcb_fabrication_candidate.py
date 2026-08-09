"""Validate HR-V0-WD-FAB-P0.1 without granting release authority."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3"
OUT = ROOT / "release" / "hr-v0" / "watchdog-pcb-fabrication-candidate-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
BOARD_REFS = {
    "CDEC1", "CDRV1", "CDRV2", "CFI1", "CFI2", "DC1", "ISO1", "JWF1", "JWH1", "JWP1",
    "RHB1", "RHP1", "RPD1", "RPD2", "RSN1", "RSN2", "RSO1", "RSO2", "RTH1", "RTH2",
    "RW1", "RW2", "UDRV1", "UDRV2", "UFB1", "WDCTRL1", *{f"TP{i}" for i in range(1, 17)},
}
EXPECTED_GERBERS = {
    "project-button-v3-F_Cu.gtl", "project-button-v3-B_Cu.gbl", "project-button-v3-F_Paste.gtp",
    "project-button-v3-B_Paste.gbp", "project-button-v3-F_Silkscreen.gto",
    "project-button-v3-B_Silkscreen.gbo", "project-button-v3-F_Mask.gts",
    "project-button-v3-B_Mask.gbs", "project-button-v3-Edge_Cuts.gm1", "project-button-v3-job.gbrjob",
}
EXPECTED_DRILL = {
    "project-button-v3-PTH.drl", "project-button-v3-NPTH.drl", "project-button-v3-PTH-drl_map.svg",
    "project-button-v3-NPTH-drl_map.svg", "project-button-v3-drill-report.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def need(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    required = {
        "README.md", "index.html", "assembly-bom.csv", "fabrication-parameters.csv", "fabrication-holds.csv",
        "source-register.csv", "package-status.json", "file-manifest.csv", "source/project-button-v3.kicad_pcb",
        "source/project-button-v3.kicad_pro", "cam/project-button-v3-drc.rpt",
        "cam/project-button-v3-all-pos.csv", "cam/project-button-v3.d356", "cam/project-button-v3-stats.json",
        "cam/kicad-cli.log",
    }
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(required <= actual, f"missing required files: {sorted(required - actual)}", failures)
    need(not any(path.suffix.lower() == ".zip" for path in OUT.rglob("*")), "archive/upload bundle must not exist", failures)

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-WD-FAB-P0.1", "wrong package identifier", failures)
    need(status.get("cam_generated") is True, "CAM generation not recorded", failures)
    for key in ("cam_released", "supplier_selected", "portal_upload_authorized", "fabrication_order_authorized",
                "assembly_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must be false", failures)
    need(status.get("open_holds") == 14, "status must record 14 open holds", failures)

    controlled_board = OUT / "source" / "project-button-v3.kicad_pcb"
    # R89 advanced the live source to PCB-P0.6; R132 advanced it to PCB-P0.7;
    # R138/R139 add field metadata only as PCB-P0.8/P0.9. The R88 package is immutable
    # historical evidence and must now differ from, never masquerade as, the
    # current source. Its own file manifest still protects every stored byte.
    need(sha256(controlled_board) != sha256(SOURCE / controlled_board.name),
         "historical PCB-P0.5 unexpectedly equals current PCB-P0.9 source", failures)
    need(sha256(OUT / "source" / "project-button-v3.kicad_pro") != sha256(SOURCE / "project-button-v3.kicad_pro"),
         "historical project unexpectedly equals current land-corrected project", failures)
    need('rev "PCB-P0.9 / Electrical V3-P1.14"' in (SOURCE / controlled_board.name).read_text(encoding="utf-8-sig"),
         "live source is not the controlled metadata-only PCB-P0.9 successor", failures)
    board = pcbnew.LoadBoard(str(controlled_board))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(set(footprints) == BOARD_REFS | {"MH1", "MH2", "MH3", "MH4"}, "board footprint membership changed", failures)
    need(len(list(board.GetTracks())) == 257, "board must contain 201 segments plus 56 vias", failures)
    need(sum(1 for item in board.GetTracks() if isinstance(item, pcbnew.PCB_VIA)) == 56, "board must contain 56 vias", failures)
    need(len(board.Zones()) == 3, "board must contain three zones", failures)
    # Edge bounding boxes include the plotted line width; exact finished dimensions
    # are independently checked in the KiCad-generated statistics below.
    board_text = controlled_board.read_text(encoding="utf-8")
    need(WARNING in board_text, "source board warning missing", failures)

    drc = (OUT / "cam" / "project-button-v3-drc.rpt").read_text(encoding="utf-8")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc and "Found 0 Footprint errors" in drc,
         "fresh DRC is not zero", failures)
    gerbers = {path.name for path in (OUT / "cam" / "gerbers").iterdir() if path.is_file()}
    drills = {path.name for path in (OUT / "cam" / "drill").iterdir() if path.is_file()}
    need(gerbers == EXPECTED_GERBERS, f"Gerber membership mismatch: {sorted(gerbers ^ EXPECTED_GERBERS)}", failures)
    need(drills == EXPECTED_DRILL, f"drill membership mismatch: {sorted(drills ^ EXPECTED_DRILL)}", failures)
    for name in EXPECTED_GERBERS | EXPECTED_DRILL:
        base = OUT / "cam" / ("gerbers" if name in EXPECTED_GERBERS else "drill") / name
        need(base.stat().st_size > 100, f"empty/truncated CAM file: {name}", failures)
    need("M48" in (OUT / "cam" / "drill" / "project-button-v3-PTH.drl").read_text(encoding="ascii"), "invalid PTH drill header", failures)
    d356 = (OUT / "cam" / "project-button-v3.d356").read_text(encoding="ascii", errors="replace")
    need(d356.startswith("P  CODE 00") and "P  UNITS" in d356 and "317" in d356, "invalid IPC-D-356 output", failures)

    positions = read_csv(OUT / "cam" / "project-button-v3-all-pos.csv")
    need({row["Ref"] for row in positions} == BOARD_REFS, "position file must cover exactly 42 assembly references", failures)
    bom = read_csv(OUT / "assembly-bom.csv")
    bom_refs = {ref for row in bom for ref in row["references"].split()}
    need(bom_refs == BOARD_REFS, "assembly BOM must cover exactly 42 references", failures)
    need(all(row["release_state"] == "NOT RELEASED" for row in bom), "BOM release state changed", failures)

    holds = read_csv(OUT / "fabrication-holds.csv")
    need(len(holds) == 14, "expected 14 fabrication holds", failures)
    need(all(row["state"] == "OPEN" and row["closure_evidence"] == "NONE" for row in holds), "all fabrication holds must remain open", failures)
    sources = read_csv(OUT / "source-register.csv")
    need(len(sources) == 3 and all(row["url"].startswith("https://docs.oshpark.com/") for row in sources), "source register changed", failures)

    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:16px" in page, "interactive guide body text below required baseline", failures)
    need("No supplier upload. No order. No assembly. No energization. No safety credit." in page, "guide authorization warning missing", failures)
    need(page.count("WD-FAB-HOLD-") == 14, "guide does not show all 14 holds", failures)
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "not a manufacturing release" in readme, "README warning/release state missing", failures)

    manifest = read_csv(OUT / "file-manifest.csv")
    manifest_paths = {row["path"] for row in manifest}
    expected_manifest = actual - {"file-manifest.csv"}
    need(manifest_paths == expected_manifest, f"manifest membership mismatch: {sorted(manifest_paths ^ expected_manifest)}", failures)
    for row in manifest:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path), f"manifest hash mismatch: {row['path']}", failures)
        need(int(row["bytes"]) == path.stat().st_size, f"manifest size mismatch: {row['path']}", failures)

    log = (OUT / "cam" / "kicad-cli.log").read_text(encoding="utf-8")
    need(log.count("exit=0") == 6, "expected six successful KiCad CLI operations", failures)
    stats = json.loads((OUT / "cam" / "project-button-v3-stats.json").read_text(encoding="utf-8"))
    need(stats["metadata"]["generator"] == "KiCad 10.0.5", "wrong KiCad generator version", failures)
    need(stats["board"]["width"] == "160.0000 mm" and stats["board"]["height"] == "100.0000 mm", "stats outline mismatch", failures)

    if failures:
        print("HR-V0-WD-FAB-P0.1 FAIL")
        for failure in failures:
            print(" -", failure)
        return 1
    print("HR-V0-WD-FAB-P0.1 HISTORICAL RECORD PASS")
    print("  42 assembly references + 4 mechanical holes; zero native DRC violations")
    print("  deterministic Gerber/drill/position/IPC-D-356 outputs; 14 holds OPEN")
    print("  superseded by metadata-only PCB-P0.9 for current review; do not upload or order PCB-P0.5")
    print("  fabrication, assembly, energization and safety credit remain prohibited")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
