"""Fail-closed checks for the HR-30 Boston fabrication route."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "boston-fabrication-route-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_boston_fabrication_route_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stl_summary(path: Path) -> tuple[int, tuple[float, float, float]]:
    data = path.read_bytes()
    need(len(data) >= 84, "short BPL STL")
    count = struct.unpack_from("<I", data, 80)[0]
    need(len(data) == 84 + 50 * count, "BPL STL binary structure drift")
    vertices = []
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + 50 * index)
        vertices.extend((values[3:6], values[6:9], values[9:12]))
    bbox = tuple(max(v[axis] for v in vertices) - min(v[axis] for v in vertices) for axis in range(3))
    return count, bbox


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    status = json.loads((OUT / "route-status.json").read_text(encoding="utf-8"))
    sources = rows(OUT / "primary-source-register.csv")
    facilities = rows(OUT / "facility-capability-register.csv")
    screen = rows(OUT / "bpl-envelope-screen.csv")
    plate_rows = rows(OUT / "bpl-submission" / "plate-part-register.csv")
    actions = rows(OUT / "execution-action-register.csv")
    holds = rows(OUT / "open-holds.csv")
    rfq = rows(OUT / "commercial-rfq-routing.csv")
    need(len(sources) == 11 and all(r["url"].startswith("https://") and r["accessed_date"] == "2026-08-17" for r in sources), "primary-source register drift")
    need(len(facilities) == 8 and {r["route_id"] for r in facilities} == {f"BFR-R{i:02d}" for i in range(1, 9)}, "facility routes drift")
    bpl = facilities[0]
    need("TEMPORARILY UNAVAILABLE" in bpl["current_state"] and "146 x 146 x 146" in bpl["verified_capability"] and "<=7 hours" in bpl["access_boundary"], "BPL boundary overclaimed")
    need(len(screen) == 98 and all(r["bpl_7_hour_limit_verified"].startswith("NO") for r in screen), "98-part BPL screen incomplete")
    need(len(plate_rows) == 9 and len({r["part_id"] for r in plate_rows}) == 9 and all(r["scale"].startswith("1:1") for r in plate_rows), "gripper plate part set drift")
    stl = OUT / "bpl-submission" / "HR30_G01_gripper_fit_plate_nonstructural.stl"
    triangle_count, bbox = stl_summary(stl)
    need(triangle_count == status["bpl_gripper_plate_triangle_count"], "plate triangle count drift")
    need(all(value <= 140.0 + 1e-4 for value in bbox), f"plate exceeds conservative envelope: {bbox}")
    need(sha(stl) == status["bpl_gripper_plate_sha256"], "plate hash drift")
    bundle = OUT / "makerspace-submission" / "HR30_complete_98_part_nonstructural_fit_check.zip"
    need(sha(bundle) == status["complete_fit_check_zip_sha256"], "bundle hash drift")
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        need(len([name for name in names if name.lower().endswith(".stl")]) == 98, "bundle requires 98 STLs")
        need(not any(name.lower().endswith((".gcode", ".3mf")) for name in names), "unreleased slicer artifact present")
        need(len(set(names)) == len(names), "duplicate ZIP member")
    need(len(actions) == 5 and all(r["state"] == "OPEN" for r in actions), "execution sequence drift")
    need(len(holds) == 6 and all(r["state"] == "OPEN" for r in holds), "open holds drift")
    need(len(rfq) == 5 and all(r["execution_state"] == "NO CONTACT / NO QUOTE" for r in rfq), "RFQ state overclaimed")
    for key in [
        "bpl_service_currently_available", "bpl_print_time_verified", "makerspace_capability_confirmed",
        "supplier_contact_executed", "quotes_received", "materials_selected", "structural_fabrication_released",
        "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority",
        "motion_authority", "energization_authority",
    ]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["fit_check_parts_built"] == 0 and status["fit_check_parts_inspected"] == 0, "physical execution invented")
    need((OUT / "boston-fabrication-route-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(sorted(row["path"] for row in manifest) == expected, "manifest membership drift")
    need(all(int(row["bytes"]) == (OUT / row["path"]).stat().st_size and row["sha256"] == sha(OUT / row["path"]) for row in manifest), "manifest hash/size drift")
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    need(source_files == release_files and all(sha(OUT / path) == sha(RELEASE / path) for path in source_files), "source/release parity drift")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "temporarily unavailable" in page.lower(), "web guide content/legibility drift")
    root_page = (WB / "index.html").read_text(encoding="utf-8")
    need("HR30-BOSTON-FABRICATION-ROUTE-P01-START" in root_page and "98 STLs" in root_page, "whole-body integration missing")
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["boston_fabrication_route_present"] is True and root_status["boston_fit_check_parts_built"] == 0, "root status integration drift")
    print(f"PASS: Boston route packages a {bbox[0]:.1f} x {bbox[1]:.1f} x {bbox[2]:.1f} mm nine-part gripper plate and 98-STL makerspace bundle; BPL unavailable, contacts/quotes/build/authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
