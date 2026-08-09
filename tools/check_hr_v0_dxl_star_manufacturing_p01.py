"""Validate HR-V0-DXL-STAR-MFG-P0.1 without granting work authority."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star"
OUT = ROOT / "release" / "hr-v0" / "dxl-star-manufacturing-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
CONNECTOR_REFS = {"JC1", "JP1", "JP2", "JP3", "JA1", "JA2", "JA3"}
MECHANICAL_REFS = {"MH1", "MH2", "MH3", "MH4"}
STEM = "hr-v0-dxl-star"
EXPECTED_GERBERS = {
    f"{STEM}-F_Cu.gtl", f"{STEM}-B_Cu.gbl", f"{STEM}-F_Paste.gtp", f"{STEM}-B_Paste.gbp",
    f"{STEM}-F_Silkscreen.gto", f"{STEM}-B_Silkscreen.gbo", f"{STEM}-F_Mask.gts",
    f"{STEM}-B_Mask.gbs", f"{STEM}-Edge_Cuts.gm1", f"{STEM}-job.gbrjob",
}
EXPECTED_DRILL = {
    f"{STEM}-PTH.drl", f"{STEM}-NPTH.drl", f"{STEM}-PTH-drl_map.svg",
    f"{STEM}-NPTH-drl_map.svg", f"{STEM}-drill-report.txt",
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


def pad_net(footprint, terminal: str) -> str:
    pads = [pad for pad in footprint.Pads() if pad.GetNumber() == terminal]
    if len(pads) != 1:
        raise RuntimeError(f"expected one pad {footprint.GetReference()}.{terminal}, found {len(pads)}")
    return pads[0].GetNetname()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    required = {
        "README.md", "index.html", "package-status.json", "file-manifest.csv", "cam-output-register.csv",
        "assembly-bom-register.csv", "terminal-parity-register.csv", "mechanical-feature-register.csv",
        "placement-parity-register.csv", "position-transform.json", "manufacturing-input-register.csv",
        "manufacturing-release-holds.csv", f"cam/{STEM}-drc.rpt", f"cam/{STEM}-all-pos.csv",
        f"cam/{STEM}.d356", f"cam/{STEM}-stats.json", "cam/kicad-cli.log",
    }
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(required <= actual, f"missing required files: {sorted(required - actual)}")
    need(not any(path.suffix.lower() in {".zip", ".7z", ".rar"} for path in OUT.rglob("*")), "upload archive must not exist")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-STAR-MFG-P0.1", "wrong identifier")
    need(status.get("round") == "R151", "wrong round")
    need(status.get("board") == "DXL-STAR-P0.1", "wrong board identity")
    need(status.get("native_tool") == "KiCad 10.0.5", "wrong native tool")
    need(status.get("populated_references") == 7 and status.get("connector_terminals") == 18 and status.get("mechanical_features") == 4, "wrong board counts")
    need(status.get("gerber_and_job_files") == 10 and status.get("drill_map_report_files") == 5, "wrong CAM counts")
    need(status.get("position_parity_references") == 7 and status.get("terminal_parity_rows") == 18, "wrong parity counts")
    need(status.get("position_parity_max_error_mm") == 0.0 and status.get("position_parity_max_rotation_error_deg") == 0.0, "position parity is not exact")
    need(status.get("open_holds") == 18, "wrong open-hold count")
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
    electrical_product = next((item for item in release.get("current_products", []) if item.get("domain") == "electrical"), {})
    bom_product = next((item for item in release.get("current_products", []) if item.get("domain") == "bill_of_materials"), {})
    need("HR-V0-DXL-STAR-MFG-P0.1" not in electrical_product.get("supporting_identifiers", []), "historical P0.1 CAM remains in current electrical support")
    need("HR-V0-DXL-STAR-MFG-P0.1" not in bom_product.get("supporting_identifiers", []), "historical P0.1 CAM remains in current BOM support")
    need(any("HR-V0-DXL-STAR-MFG-P0.1" in item.get("identifier", "") and "must not be used" in item.get("disposition", "") for item in release.get("historical_or_out_of_scope_products", [])), "historical P0.1 CAM quarantine is missing")
    bom051 = next((row for row in read_csv(ROOT / "bom" / "bom.csv") if row.get("item_id") == "BOM-051"), {})
    need(
        bom051.get("baseline_status") == "exact_candidate_hold"
        and "DXL-STAR-P0.2-CARRIER-CANDIDATE" in bom051.get("manufacturer_part_number", "")
        and "current manufacturing data SELECTION REQUIRED" in bom051.get("manufacturer_part_number", "")
        and "P0.1 CAM package is historical" in bom051.get("selection_basis", "")
        and "connector/current" in bom051.get("selection_basis", ""),
        "BOM-051 does not retain current P0.2 hold and historical P0.1 boundary",
    )
    gates = {row["gate_id"]: row for row in read_csv(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    need(
        gates.get("EG-004", {}).get("status") == "partial"
        and "release/hr-v0/dxl-star-manufacturing-p0.1/" in gates.get("EG-004", {}).get("evidence_location", "")
        and "tools/check_hr_v0_dxl_star_manufacturing_p01.py" in gates.get("EG-004", {}).get("evidence_location", ""),
        "EG-004 does not retain partial status with DXL-star package evidence",
    )
    need(
        gates.get("EG-015", {}).get("status") == "partial"
        and "terminal-parity-register.csv" in gates.get("EG-015", {}).get("evidence_location", ""),
        "EG-015 does not retain partial status with terminal-parity evidence",
    )

    source_map = {
        "electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pcb": SOURCE / "hr-v0-dxl-star.kicad_pcb",
        "electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pro": SOURCE / "hr-v0-dxl-star.kicad_pro",
        "electrical/kicad/hr-v0-dxl-star/bom.csv": SOURCE / "bom.csv",
        "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv": SOURCE / "connector-schedule.csv",
    }
    need(set(status.get("source_hashes", {})) == set(source_map), "source-hash membership mismatch")
    for key, path in source_map.items():
        need(status.get("source_hashes", {}).get(key) == sha256(path), f"source hash mismatch: {key}")

    board_path = SOURCE / "hr-v0-dxl-star.kicad_pcb"
    board_text = board_path.read_text(encoding="utf-8-sig")
    need('gr_text "DXL-STAR-P0.1 - U2D2 VDD OMITTED"' in board_text, "native revision/identity marking changed")
    need("PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION" in board_text, "native warning missing")
    board = pcbnew.LoadBoard(str(board_path))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(set(footprints) == CONNECTOR_REFS | MECHANICAL_REFS, "native footprint membership changed")
    need(len(list(board.GetTracks())) == 17 and len(board.Zones()) == 1, "native routing membership changed")
    need(pad_net(footprints["JC1"], "1") == "ACT_0V_PE_BONDED", "JC1.1 return mapping changed")
    need(pad_net(footprints["JC1"], "2") == "", "JC1.2 must remain no-net/no-copper")
    need(pad_net(footprints["JC1"], "3") == "DXL_TTL_DATA", "JC1.3 data mapping changed")

    drc = (OUT / "cam" / f"{STEM}-drc.rpt").read_text(encoding="utf-8")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc and "Found 0 Footprint errors" in drc, "native DRC is not zero")
    gerbers = {path.name for path in (OUT / "cam" / "gerbers").iterdir() if path.is_file()}
    drills = {path.name for path in (OUT / "cam" / "drill").iterdir() if path.is_file()}
    need(gerbers == EXPECTED_GERBERS, f"Gerber membership mismatch: {sorted(gerbers ^ EXPECTED_GERBERS)}")
    need(drills == EXPECTED_DRILL, f"drill membership mismatch: {sorted(drills ^ EXPECTED_DRILL)}")
    for name in EXPECTED_GERBERS | EXPECTED_DRILL:
        folder = "gerbers" if name in EXPECTED_GERBERS else "drill"
        need((OUT / "cam" / folder / name).stat().st_size > 100, f"empty/truncated CAM file: {name}")
    need("M48" in (OUT / "cam" / "drill" / f"{STEM}-PTH.drl").read_text(encoding="ascii"), "invalid PTH drill header")
    d356 = (OUT / "cam" / f"{STEM}.d356").read_text(encoding="ascii", errors="replace")
    need(d356.startswith("P  CODE 00") and "P  UNITS" in d356, "invalid IPC-D-356 output")
    stats = json.loads((OUT / "cam" / f"{STEM}-stats.json").read_text(encoding="utf-8"))
    need(stats.get("metadata", {}).get("generator") == "KiCad 10.0.5", "wrong stats generator")
    need(stats.get("board", {}).get("width") == "100.0000 mm" and stats.get("board", {}).get("height") == "60.0000 mm", "outline mismatch")

    raw = read_csv(OUT / "cam" / f"{STEM}-all-pos.csv")
    parity = read_csv(OUT / "placement-parity-register.csv")
    need({row["Ref"] for row in raw} == CONNECTOR_REFS, "raw position membership mismatch")
    need(len(parity) == 7 and {row["reference"] for row in parity} == CONNECTOR_REFS, "placement parity membership mismatch")
    need(all(float(row["position_error_mm"]) == 0.0 and float(row["rotation_error_deg"]) == 0.0 for row in parity), "placement parity is nonzero")
    need(all(row["state"] == "PARITY PASS - INTERNAL COORDINATES ONLY - NOT MACHINE XYRS" for row in parity), "placement release boundary changed")
    transform = json.loads((OUT / "position-transform.json").read_text(encoding="utf-8"))
    need(transform.get("reference_count") == 7 and transform.get("supplier_normalized") is False and transform.get("machine_import_authorized") is False, "position transform boundary changed")

    source_bom = read_csv(SOURCE / "bom.csv")
    assembly = read_csv(OUT / "assembly-bom-register.csv")
    need(len(source_bom) == 7 and len(assembly) == 7, "assembly BOM count mismatch")
    need({row["reference"] for row in assembly} == CONNECTOR_REFS, "assembly BOM membership mismatch")
    need(all(row["assembly_state"] == "APPLICATION HOLD - NOT RELEASED" and row["warning"] == WARNING for row in assembly), "assembly release boundary changed")

    schedule = read_csv(SOURCE / "connector-schedule.csv")
    terminals = read_csv(OUT / "terminal-parity-register.csv")
    need(len(schedule) == 18 and len(terminals) == 18, "terminal count mismatch")
    schedule_map = {(row["reference"], row["terminal"]): row for row in schedule}
    terminal_map = {(row["reference"], row["terminal"]): row for row in terminals}
    need(set(schedule_map) == set(terminal_map), "terminal membership mismatch")
    for key, row in terminal_map.items():
        scheduled = schedule_map[key]
        expected_native = "" if scheduled["net"] == "INTENTIONALLY_UNUSED_U2D2_VDD" else scheduled["net"]
        native = pad_net(footprints[key[0]], key[1])
        need(row["schedule_net"] == scheduled["net"], f"schedule net changed: {key}")
        need(native == expected_native, f"native pad net differs from schedule: {key}")
        need(row["native_pad_net"] == (native or "NO_NET_NO_COPPER") and row["parity"] == "PASS", f"recorded terminal parity changed: {key}")
    need(terminal_map[("JC1", "2")]["native_pad_net"] == "NO_NET_NO_COPPER", "JC1.2 deliberate omission not explicit")

    mechanical = read_csv(OUT / "mechanical-feature-register.csv")
    need(len(mechanical) == 4 and {row["reference"] for row in mechanical} == MECHANICAL_REFS, "mechanical feature register mismatch")
    need(all(row["feature"] == "NPTH mounting hole" and row["release_state"] == "DIMENSIONAL REVIEW REQUIRED - NOT RELEASED" for row in mechanical), "mechanical release boundary changed")

    holds = read_csv(OUT / "manufacturing-release-holds.csv")
    need(len(holds) == 18 and len({row["hold_id"] for row in holds}) == 18, "hold register must contain 18 unique rows")
    need(all(row["status"] == "OPEN" and row["warning"] == WARNING for row in holds), "all manufacturing holds must remain open")
    inputs = read_csv(OUT / "manufacturing-input-register.csv")
    need(len(inputs) == 18, "manufacturing input register must contain 18 rows")
    need(sum(row["candidate_value"] == "SELECTION REQUIRED" for row in inputs) == 11, "expected eleven explicit manufacturing selections")
    need(all(row["warning"] == WARNING for row in inputs), "manufacturing warning changed")

    outputs = read_csv(OUT / "cam-output-register.csv")
    expected_outputs = {path.relative_to(OUT).as_posix() for path in [*(p for p in (OUT / "cam" / "gerbers").glob("*") if p.is_file()), *(p for p in (OUT / "cam" / "drill").glob("*") if p.is_file()), OUT / "cam" / f"{STEM}-all-pos.csv", OUT / "cam" / f"{STEM}.d356", OUT / "cam" / f"{STEM}-stats.json", OUT / "cam" / f"{STEM}-drc.rpt"]}
    need({row["path"] for row in outputs} == expected_outputs, "CAM output register membership mismatch")
    for row in outputs:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path) and int(row["bytes"]) == path.stat().st_size, f"CAM identity mismatch: {row['path']}")
        need(row["release_state"] == "INTERNAL REVIEW ONLY - NOT RELEASED TO SUPPLIER", f"CAM release state changed: {row['path']}")

    log = (OUT / "cam" / "kicad-cli.log").read_text(encoding="utf-8")
    need(log.count("exit=0") == 6, "expected six successful KiCad CLI operations")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "code{font-size:14px", "DXL-STAR-P0.1 CAM exists for review", "quarantined internal evidence", "NOT MACHINE XYRS", "Eighteen holds remain open", "supplier releases or work authorizations"):
        need(token in page, f"guide token missing: {token}")
    need(page.count("DXL-MFG-HOLD-") == 18, "guide does not show all holds")
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "not a supplier packet" in readme and "no machine-ready assembler XYRS" in readme, "README boundary missing")

    manifest = read_csv(OUT / "file-manifest.csv")
    expected_manifest = actual - {"file-manifest.csv"}
    need({row["path"] for row in manifest} == expected_manifest, "file manifest membership mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path) and int(row["bytes"]) == path.stat().st_size, f"manifest identity mismatch: {row['path']}")

    if failures:
        print("HR-V0-DXL-STAR-MFG-P0.1 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-STAR-MFG-P0.1 PASS")
    print("  DXL-STAR-P0.1 source bound; native DRC 0; 10 Gerber/job + 5 drill/map/report files")
    print("  7 connector placements and 18 terminals at exact encoded parity; JC1.2 remains no-net/no-copper")
    print("  18 holds OPEN; no supplier contact, upload, quotation, fabrication, assembly, connection, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
