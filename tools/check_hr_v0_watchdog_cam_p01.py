"""Validate an HR-V0 watchdog CAM review package without granting work authority."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3"
P115_SOURCE = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"
P115_PARITY = ROOT / "release" / "hr-v0" / "e2-p115-parity-p0.1"
ASSEMBLY = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
PROFILE = os.environ.get("HR_V0_WD_CAM_PROFILE", "p0.1")
if PROFILE not in {"p0.1", "p0.2"}:
    raise ValueError(f"unsupported watchdog CAM profile: {PROFILE}")
CURRENT_P115 = PROFILE == "p0.2"
OUT = ROOT / "release" / "hr-v0" / f"watchdog-pcb-cam-{PROFILE}"
IDENTIFIER = f"HR-V0-WD-CAM-{PROFILE.upper()}"
ROUND = "R166" if CURRENT_P115 else "R150"
BOARD_BINDING = (
    "PCB-P0.9 / Electrical V3-P1.15-CARRIER-CANDIDATE via HR-V0-E2-P115-PARITY-P0.1"
    if CURRENT_P115
    else "PCB-P0.9 / Electrical V3-P1.14"
)
TITLE_TOKEN = "P1.15-bound PCB-P0.9 CAM exists for review" if CURRENT_P115 else "Current PCB-P0.9 CAM exists for review"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    required = {
        "README.md", "index.html", "package-status.json", "file-manifest.csv", "cam-output-register.csv",
        "cam-assembly-parity.csv", "position-transform.json", "manufacturing-input-register.csv",
        "cam-release-holds.csv",
        "cam/project-button-v3-drc.rpt", "cam/project-button-v3-all-pos.csv",
        "cam/project-button-v3.d356", "cam/project-button-v3-stats.json", "cam/kicad-cli.log",
    }
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(required <= actual, f"missing required files: {sorted(required - actual)}")
    need(not any(path.suffix.lower() in {".zip", ".7z", ".rar"} for path in OUT.rglob("*")), "upload archive must not exist")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER, "wrong identifier")
    need(status.get("round") == ROUND, "wrong round")
    need(status.get("board") == BOARD_BINDING, "wrong board identity")
    need(status.get("native_board_title_revision") == "PCB-P0.9 / Electrical V3-P1.14", "native board title boundary changed")
    need(
        status.get("current_electrical_baseline")
        == ("Project Button Electrical V3-P1.15-CARRIER-CANDIDATE" if CURRENT_P115 else "Project Button Electrical V3-P1.14"),
        "wrong electrical baseline",
    )
    need(
        status.get("p115_parity_evidence") == ("HR-V0-E2-P115-PARITY-P0.1" if CURRENT_P115 else None),
        "wrong P1.15 parity binding",
    )
    need(status.get("assembly_data") == "HR-V0-WD-PCBA-DATA-P0.2", "wrong assembly-data identity")
    need(status.get("native_tool") == "KiCad 10.0.5", "wrong native tool")
    need(status.get("populated_references") == 42 and status.get("mechanical_features") == 4, "wrong board counts")
    need(status.get("gerber_and_job_files") == 10 and status.get("drill_map_report_files") == 5, "wrong CAM counts")
    need(status.get("position_parity_references") == 42, "wrong position-parity count")
    need(status.get("position_parity_max_error_mm") == 0.0, "position parity is not exact")
    need(status.get("position_parity_max_rotation_error_deg") == 0.0, "rotation parity is not exact")
    need(status.get("open_holds") == 18, "wrong hold count")
    need(status.get("cam_generated") is True and status.get("cam_review_only") is True, "CAM review state missing")
    for key in (
        "cam_released", "supplier_normalized_xyrs_exists", "supplier_selected", "supplier_contacted",
        "files_uploaded", "quotation_requested", "fabrication_authorized", "assembly_authorized",
        "physical_article_exists", "connection_authorized", "motion_authorized", "energization_authorized",
        "safety_credit",
    ):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    electrical_product = next(
        (item for item in release.get("current_products", []) if item.get("domain") == "electrical"), {}
    )
    historical_products = release.get("historical_or_out_of_scope_products", [])
    if CURRENT_P115:
        need(
            IDENTIFIER in electrical_product.get("supporting_identifiers", []),
            "release candidate omits the current P1.15-bound CAM-review package",
        )
        need(
            any("HR-V0-WD-CAM-P0.1" in item.get("identifier", "") for item in historical_products),
            "release candidate omits the superseded P0.1 CAM boundary",
        )
    else:
        need(
            IDENTIFIER in electrical_product.get("supporting_identifiers", [])
            or any(IDENTIFIER in item.get("identifier", "") for item in historical_products),
            "release candidate omits the controlled historical CAM-review package",
        )
        need(
            any(
                "V3-P1.14" in item.get("identifier", "")
                and "historical review evidence" in item.get("disposition", "")
                for item in historical_products
            ),
            "release candidate omits the P1.14 historical source boundary",
        )
    gates = {row["gate_id"]: row for row in read_csv(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    eg004 = gates.get("EG-004", {})
    need(
        eg004.get("status") == "partial"
        and f"release/hr-v0/watchdog-pcb-cam-{PROFILE}/" in eg004.get("evidence_location", "")
        and f"tools/check_hr_v0_watchdog_cam_{PROFILE.replace('.', '')}.py" in eg004.get("evidence_location", ""),
        "EG-004 does not retain partial status with current CAM evidence",
    )
    bom048 = next((row for row in read_csv(ROOT / "bom" / "bom.csv") if row.get("item_id") == "BOM-048"), {})
    need(
        bom048.get("baseline_status") == "exact_candidate_hold"
        and (IDENTIFIER in bom048.get("selection_basis", "") if CURRENT_P115 else True)
        and "not supplier-released" in bom048.get("selection_basis", ""),
        "BOM-048 does not retain exact hold with quarantined current CAM evidence",
    )

    source_map = {
        "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb": SOURCE / "project-button-v3.kicad_pcb",
        "electrical/kicad/project-button-v3/project-button-v3.kicad_pro": SOURCE / "project-button-v3.kicad_pro",
        "electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/board-assembly-bom.csv": ASSEMBLY / "board-assembly-bom.csv",
        "electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-placement-reference.csv": ASSEMBLY / "assembly-placement-reference.csv",
        "electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/mechanical-feature-register.csv": ASSEMBLY / "mechanical-feature-register.csv",
        "electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-data-holds.csv": ASSEMBLY / "assembly-data-holds.csv",
    }
    if CURRENT_P115:
        source_map.update(
            {
                "electrical/kicad/project-button-v3-p1.15-carrier-candidate/project-button-v3-p1.15-carrier-candidate.kicad_pro": P115_SOURCE / "project-button-v3-p1.15-carrier-candidate.kicad_pro",
                "electrical/kicad/project-button-v3-p1.15-carrier-candidate/project-button-v3-p1.15-carrier-candidate.kicad_sch": P115_SOURCE / "project-button-v3-p1.15-carrier-candidate.kicad_sch",
                "electrical/kicad/project-button-v3-p1.15-carrier-candidate/SOURCE-MANIFEST.csv": P115_SOURCE / "SOURCE-MANIFEST.csv",
                "release/hr-v0/e2-p115-parity-p0.1/package-status.json": P115_PARITY / "package-status.json",
                "release/hr-v0/e2-p115-parity-p0.1/expected-change-register.csv": P115_PARITY / "expected-change-register.csv",
                "release/hr-v0/e2-p115-parity-p0.1/source-hash-register.csv": P115_PARITY / "source-hash-register.csv",
            }
        )
    need(set(status.get("source_hashes", {})) == set(source_map), "source-hash membership mismatch")
    for key, path in source_map.items():
        need(status.get("source_hashes", {}).get(key) == sha256(path), f"source hash mismatch: {key}")
    controlled_board = SOURCE / "project-button-v3.kicad_pcb"
    board_text = controlled_board.read_text(encoding="utf-8-sig")
    need('rev "PCB-P0.9 / Electrical V3-P1.14"' in board_text, "controlled board revision changed")
    need("PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION" in board_text, "native board warning missing")
    board = pcbnew.LoadBoard(str(controlled_board))
    footprints = {footprint.GetReference() for footprint in board.GetFootprints()}
    need(footprints == BOARD_REFS | {"MH1", "MH2", "MH3", "MH4"}, "footprint membership mismatch")
    need(len(list(board.GetTracks())) == 257, "track/via membership changed")
    need(sum(isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks()) == 56, "via count changed")
    need(len(board.Zones()) == 3, "zone count changed")

    drc = (OUT / "cam" / "project-button-v3-drc.rpt").read_text(encoding="utf-8")
    need(
        "Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc and "Found 0 Footprint errors" in drc,
        "native DRC is not zero",
    )
    gerbers = {path.name for path in (OUT / "cam" / "gerbers").iterdir() if path.is_file()}
    drills = {path.name for path in (OUT / "cam" / "drill").iterdir() if path.is_file()}
    need(gerbers == EXPECTED_GERBERS, f"Gerber membership mismatch: {sorted(gerbers ^ EXPECTED_GERBERS)}")
    need(drills == EXPECTED_DRILL, f"drill membership mismatch: {sorted(drills ^ EXPECTED_DRILL)}")
    for name in EXPECTED_GERBERS | EXPECTED_DRILL:
        path = OUT / "cam" / ("gerbers" if name in EXPECTED_GERBERS else "drill") / name
        need(path.stat().st_size > 100, f"empty/truncated CAM file: {name}")
    need("M48" in (OUT / "cam" / "drill" / "project-button-v3-PTH.drl").read_text(encoding="ascii"), "invalid PTH drill header")
    d356 = (OUT / "cam" / "project-button-v3.d356").read_text(encoding="ascii", errors="replace")
    need(d356.startswith("P  CODE 00") and "P  UNITS" in d356, "invalid IPC-D-356 output")
    stats = json.loads((OUT / "cam" / "project-button-v3-stats.json").read_text(encoding="utf-8"))
    need(stats.get("metadata", {}).get("generator") == "KiCad 10.0.5", "wrong stats generator")
    need(stats.get("board", {}).get("width") == "160.0000 mm" and stats.get("board", {}).get("height") == "100.0000 mm", "outline mismatch")
    need(stats.get("board", {}).get("board_thickness") == "1.6000 mm", "native thickness setting changed")

    raw_positions = read_csv(OUT / "cam" / "project-button-v3-all-pos.csv")
    parity = read_csv(OUT / "cam-assembly-parity.csv")
    need({row["Ref"] for row in raw_positions} == BOARD_REFS, "raw position membership mismatch")
    need(len(parity) == 42 and {row["reference"] for row in parity} == BOARD_REFS, "parity membership mismatch")
    need(all(float(row["position_error_mm"]) == 0.0 for row in parity), "nonzero position parity error")
    need(all(float(row["rotation_error_deg"]) == 0.0 for row in parity), "nonzero rotation parity error")
    need(all(row["state"] == "PARITY PASS - INTERNAL COORDINATES ONLY - NOT MACHINE XYRS" for row in parity), "parity release state changed")
    transform = json.loads((OUT / "position-transform.json").read_text(encoding="utf-8"))
    need(transform.get("reference_count") == 42, "transform reference count changed")
    need(transform.get("x_offset_mm") == 20.0 and transform.get("inverted_y_offset_mm") == 20.0, "derived transform changed")
    need(transform.get("supplier_normalized") is False and transform.get("machine_import_authorized") is False, "transform boundary changed")

    assembly_bom = read_csv(ASSEMBLY / "board-assembly-bom.csv")
    need(len(assembly_bom) == 16 and sum(int(row["quantity_per_board"]) for row in assembly_bom) == 42, "assembly BOM mismatch")
    need(len(read_csv(ASSEMBLY / "mechanical-feature-register.csv")) == 4, "mechanical-feature count mismatch")
    holds = read_csv(OUT / "cam-release-holds.csv")
    need(len(holds) == 18, "hold register must contain 18 rows")
    need(all(row["status"] == "OPEN" and row["warning"] == WARNING for row in holds), "all holds must remain open")
    inputs = read_csv(OUT / "manufacturing-input-register.csv")
    need(len(inputs) == 18, "manufacturing input register must contain 18 rows")
    need(sum(row["candidate_value"] == "SELECTION REQUIRED" for row in inputs) == 11, "expected eleven explicit manufacturing selections")
    need(all(row["warning"] == WARNING for row in inputs), "manufacturing warning changed")

    output_register = read_csv(OUT / "cam-output-register.csv")
    expected_outputs = {
        path.relative_to(OUT).as_posix()
        for path in [
            *(p for p in (OUT / "cam" / "gerbers").glob("*") if p.is_file()),
            *(p for p in (OUT / "cam" / "drill").glob("*") if p.is_file()),
            OUT / "cam" / "project-button-v3-all-pos.csv",
            OUT / "cam" / "project-button-v3.d356",
            OUT / "cam" / "project-button-v3-stats.json",
            OUT / "cam" / "project-button-v3-drc.rpt",
        ]
    }
    need({row["path"] for row in output_register} == expected_outputs, "CAM output-register membership mismatch")
    for row in output_register:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path), f"CAM hash mismatch: {row['path']}")
        need(int(row["bytes"]) == path.stat().st_size, f"CAM size mismatch: {row['path']}")
        need(row["release_state"] == "INTERNAL REVIEW ONLY - NOT RELEASED TO SUPPLIER", f"CAM release state changed: {row['path']}")

    log = (OUT / "cam" / "kicad-cli.log").read_text(encoding="utf-8")
    need(log.count("exit=0") == 6, "expected six successful KiCad CLI operations")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (
        "font:clamp(16px", "code{font-size:14px", TITLE_TOKEN,
        "quarantined internal evidence", "NOT MACHINE XYRS", "Eighteen holds remain open",
        "supplier releases or work authorizations",
    ):
        need(token in page, f"guide token missing: {token}")
    need(page.count("WD-DATA-HOLD-") == 12 and page.count("WD-CAM-HOLD-") == 6, "guide does not show all holds")
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "no machine-ready assembler XYRS" in readme, "README boundary missing")

    manifest = read_csv(OUT / "file-manifest.csv")
    expected_manifest = actual - {"file-manifest.csv"}
    need({row["path"] for row in manifest} == expected_manifest, "file-manifest membership mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path), f"manifest hash mismatch: {row['path']}")
        need(int(row["bytes"]) == path.stat().st_size, f"manifest size mismatch: {row['path']}")

    if failures:
        print(f"{IDENTIFIER} check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS")
    print("  PCB-P0.9 source bound; native DRC 0; 10 Gerber/job + 5 drill/map/report files")
    print("  42 internal position rows at exact parity; supplier-normalized XYRS remains absent")
    print("  18 holds OPEN; no supplier contact, upload, quotation, fabrication, assembly, connection, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
