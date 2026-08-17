"""Fail-closed checks for the 98-part HR-30 full-scale fit-check kit."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
import tempfile
import zipfile
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "full-scale-fit-check-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_full_scale_fit_check_p01.py"
MODULES = {"H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"}


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_stl(path: Path) -> tuple[int, tuple[float, float, float], tuple[float, float, float], float]:
    data = path.read_bytes()
    need(len(data) >= 84, f"short STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    need(count > 0 and len(data) == 84 + 50 * count, f"invalid binary STL: {path}")
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    volume6 = 0.0
    for index in range(count):
        values = struct.unpack_from("<12f", data, 84 + 50 * index)
        a, b, c = values[3:6], values[6:9], values[9:12]
        for vertex in (a, b, c):
            need(all(math.isfinite(v) for v in vertex), f"non-finite STL vertex: {path}")
            for axis, value in enumerate(vertex):
                lo[axis], hi[axis] = min(lo[axis], value), max(hi[axis], value)
        cross = (b[1] * c[2] - b[2] * c[1], b[2] * c[0] - b[0] * c[2], b[0] * c[1] - b[1] * c[0])
        volume6 += a[0] * cross[0] + a[1] * cross[1] + a[2] * cross[2]
    return count, tuple(lo), tuple(hi), abs(volume6) / 6.0


def determinant(matrix: list[list[int]]) -> int:
    a, b, c = matrix
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "fit-check source/release package missing")
    parts = rows(OUT / "fit-check-part-register.csv")
    traveler = rows(OUT / "fit-check-assembly-traveler.csv")
    inspections = rows(OUT / "fit-check-inspection-register.csv")
    batches = rows(OUT / "print-build-plate-register.csv")
    placements = rows(OUT / "plate-layout-register.csv")
    bundles = rows(OUT / "module-bundle-register.csv")
    envelopes = rows(OUT / "printer-envelope-compatibility.csv")
    issues, holds = rows(OUT / "fit-check-issue-register.csv"), rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "fit-check-status.json").read_text(encoding="utf-8"))
    need(len(parts) == 98 and len({r["part_id"] for r in parts}) == 98, "98 unique physical parts required")
    need(set(r["module"] for r in parts) == MODULES, "twelve-module whole-body coverage drift")
    need(len(batches) >= 12 and len(issues) == len(bundles) == 12 and len(holds) == 6 and len(envelopes) == 4, "plate/bundle/issue/hold/envelope coverage drift")
    need(len(placements) == 98 and len({r["part_id"] for r in placements}) == 98, "every part must have exactly one candidate plate placement")
    need(len(inspections) == 392 and len(traveler) == 54, "inspection/traveler coverage drift")
    need(all(r["built_quantity"] == "0" and r["inspection_result"] == "NOT EXECUTED" and r["structural_credit"] == "NONE" for r in parts), "physical execution or structural-credit overclaim")
    need(all(r["result"] == "NOT EXECUTED" for r in traveler + inspections), "traveler/inspection falsely executed")
    need(all(r["state"] == "OPEN - NOT EXECUTED" for r in holds), "hold falsely closed")
    with tempfile.TemporaryDirectory(prefix="hr30-fit-check-") as temporary:
        temporary_root = Path(temporary)
        for row in parts:
            source = ROOT / row["source_step_path"]
            stl = OUT / row["stl_path"]
            need(source.is_file() and sha(source) == row["source_step_sha256"], f"source STEP drift: {row['part_id']}")
            need(stl.is_file() and sha(stl) == row["stl_sha256"] and stl.stat().st_size == int(row["stl_bytes"]), f"STL hash/size drift: {row['part_id']}")
            triangle_count, lower, upper, mesh_volume = parse_stl(stl)
            mesh_bbox = tuple(upper[i] - lower[i] for i in range(3))
            need(triangle_count == int(row["triangle_count"]), f"STL triangle-count drift: {row['part_id']}")
            shape = cq.importers.importStep(str(source)).val()
            need(shape is not None and shape.Volume() > 0, f"invalid STEP shape: {row['part_id']}")
            cad = shape.BoundingBox()
            cad_bbox = (cad.xlen, cad.ylen, cad.zlen)
            raw = temporary_root / f"{row['part_id']}.stl"
            cq.exporters.export(shape, str(raw), tolerance=0.15, angularTolerance=0.15)
            need(sha(raw) == row["source_tessellation_sha256"], f"source tessellation provenance drift: {row['part_id']}")
            matrix_values = [int(value) for value in row["orientation_matrix_row_major"].split()]
            need(len(matrix_values) == 9, f"orientation matrix width drift: {row['part_id']}")
            matrix = [matrix_values[0:3], matrix_values[3:6], matrix_values[6:9]]
            need(determinant(matrix) == 1 and all(sum(abs(value) for value in matrix[row_index]) == 1 for row_index in range(3)) and all(sum(abs(matrix[row_index][column]) for row_index in range(3)) == 1 for column in range(3)), f"orientation is not a right-handed signed permutation: {row['part_id']}")
            expected_bbox = tuple(sum(abs(matrix[row_index][axis]) * cad_bbox[axis] for axis in range(3)) for row_index in range(3))
            need(all(abs(mesh_bbox[i] - expected_bbox[i]) <= 0.31 for i in range(3)), f"oriented STL/STEP bounds mismatch: {row['part_id']} {mesh_bbox} {expected_bbox}")
            need(all(abs(float(row[f"oriented_bbox_{axis}_mm"]) - mesh_bbox[i]) <= 1e-5 for i, axis in enumerate("xyz")), f"registered oriented bounds drift: {row['part_id']}")
            need(all(abs(float(row[f"step_bbox_{axis}_mm"]) - cad_bbox[i]) <= 1e-5 for i, axis in enumerate("xyz")), f"registered STEP bounds drift: {row['part_id']}")
            need(all(abs(lower[i] - target) <= 1e-4 for i, target in enumerate((5.0, 5.0, 0.0))), f"STL is not bed normalized: {row['part_id']} {lower}")
            need(upper[0] <= 215.0001 and upper[1] <= 215.0001 and upper[2] <= 250.0001, f"STL exceeds generic print envelope: {row['part_id']} {upper}")
            need(abs(float(row["mesh_volume_mm3"]) - mesh_volume) <= max(0.01, mesh_volume * 1e-6), f"registered mesh volume drift: {row['part_id']}")
            need(abs(mesh_volume - shape.Volume()) <= max(1.0, shape.Volume() * 0.005), f"tessellated/STEP volume mismatch: {row['part_id']} {mesh_volume} {shape.Volume()}")
            need(row["bed_normalized"] == "YES - X/Y MIN 5 MM; Z MIN 0 MM", f"bed-normalization state drift: {row['part_id']}")

    part_by_id = {row["part_id"]: row for row in parts}
    need(set(r["part_id"] for r in placements) == set(part_by_id), "plate placement part set drift")
    for plate in batches:
        assigned = [row for row in placements if row["plate_id"] == plate["plate_id"]]
        need(len(assigned) == int(plate["part_count"]) and assigned, f"plate part count drift: {plate['plate_id']}")
        need((OUT / plate["layout_svg"]).is_file() and "font-size=\"12\"" in (OUT / plate["layout_svg"]).read_text(encoding="utf-8"), f"plate layout missing/illegible: {plate['plate_id']}")
        for row in assigned:
            x, y, width, depth, height = (float(row[key]) for key in ("x_mm", "y_mm", "placed_width_mm", "placed_depth_mm", "part_height_mm"))
            need(x >= 5.0 and y >= 5.0 and x + width <= 215.0001 and y + depth <= 215.0001 and height <= 250.0001, f"plate placement out of bounds: {row['part_id']}")
            need(row["rotation_z_deg"] in {"0", "90"} and row["physical_layout_executed"] == "NO", f"plate transform/execution drift: {row['part_id']}")
        for left_index, left in enumerate(assigned):
            lx, ly, lw, ld = (float(left[key]) for key in ("x_mm", "y_mm", "placed_width_mm", "placed_depth_mm"))
            for right in assigned[left_index + 1:]:
                rx, ry, rw, rd = (float(right[key]) for key in ("x_mm", "y_mm", "placed_width_mm", "placed_depth_mm"))
                need(lx + lw <= rx + 1e-6 or rx + rw <= lx + 1e-6 or ly + ld <= ry + 1e-6 or ry + rd <= ly + 1e-6, f"plate bounding boxes overlap: {left['part_id']} / {right['part_id']}")

    need(any(row["envelope_id"] == "FC-ENV-220" and row["fit_part_count"] == "98" and row["excluded_part_count"] == "0" for row in envelopes), "generic 220 mm geometry compatibility not closed")
    for bundle in bundles:
        archive = OUT / bundle["zip_path"]
        need(archive.is_file() and sha(archive) == bundle["zip_sha256"] and archive.stat().st_size == int(bundle["zip_bytes"]), f"module bundle hash/size drift: {bundle['module']}")
        expected_names = {f"{bundle['module']}/{Path(row['stl_path']).name}" for row in parts if row["module"] == bundle["module"]} | {f"{bundle['module']}/README.txt"}
        with zipfile.ZipFile(archive) as zipped:
            need(set(zipped.namelist()) == expected_names and zipped.testzip() is None, f"module ZIP membership/CRC drift: {bundle['module']}")
    for key in ["whole_body_fit_check_executed", "fit_physically_validated", "structural_credit", "production_equivalence", "procurement_authority", "production_fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["physical_part_count"] == status["stl_count"] == status["bed_normalized_stl_count"] == 98 and status["module_count"] == status["module_bundle_count"] == 12, "status counts drift")
    need(status["candidate_plate_count"] == len(batches) and status["gcode_released"] is False and status["slicer_profile_selected"] is False, "plate/G-code boundary drift")
    need(status["built_part_count"] == status["inspected_part_count"] == status["assembled_module_count"] == 0, "physical count overclaim")
    need((OUT / "full-scale-fit-check-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    root = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root["full_scale_fit_check_part_count"] == root["full_scale_fit_check_stl_count"] == root["full_scale_fit_check_bed_normalized_part_count"] == 98, "root fit-check integration missing")
    need(root["full_scale_fit_check_physically_validated"] is False and root["full_scale_fit_check_structural_use_permitted"] is False, "root authority overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "font-size:14px" in page and "Print the whole robot" in page, "guide content/legibility drift")
    need("HR30-FULL-SCALE-FIT-CHECK-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    print(f"PASS: 98 source-bound full-scale STLs are bed-normalized across {len(batches)} candidate plates and 12 module bundles; {sum(int(r['triangle_count']) for r in parts):,} triangles; zero G-code, prints, inspections, structural credit or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
