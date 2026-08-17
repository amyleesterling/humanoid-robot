"""Fail-closed checks for the 98-part HR-30 full-scale fit-check kit."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
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


def parse_stl(path: Path) -> tuple[int, tuple[float, float, float]]:
    data = path.read_bytes()
    need(len(data) >= 84, f"short STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    need(count > 0 and len(data) == 84 + 50 * count, f"invalid binary STL: {path}")
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    for index in range(count):
        values = struct.unpack_from("<12f", data, 84 + 50 * index)
        for vertex in (values[3:6], values[6:9], values[9:12]):
            need(all(math.isfinite(v) for v in vertex), f"non-finite STL vertex: {path}")
            for axis, value in enumerate(vertex):
                lo[axis], hi[axis] = min(lo[axis], value), max(hi[axis], value)
    return count, tuple(hi[i] - lo[i] for i in range(3))


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "fit-check source/release package missing")
    parts = rows(OUT / "fit-check-part-register.csv")
    traveler = rows(OUT / "fit-check-assembly-traveler.csv")
    inspections = rows(OUT / "fit-check-inspection-register.csv")
    batches = rows(OUT / "print-build-plate-register.csv")
    issues, holds = rows(OUT / "fit-check-issue-register.csv"), rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "fit-check-status.json").read_text(encoding="utf-8"))
    need(len(parts) == 98 and len({r["part_id"] for r in parts}) == 98, "98 unique physical parts required")
    need(set(r["module"] for r in parts) == MODULES, "twelve-module whole-body coverage drift")
    need(len(batches) == len(issues) == 12 and len(holds) == 6, "batch/issue/hold coverage drift")
    need(len(inspections) == 392 and len(traveler) == 54, "inspection/traveler coverage drift")
    need(all(r["built_quantity"] == "0" and r["inspection_result"] == "NOT EXECUTED" and r["structural_credit"] == "NONE" for r in parts), "physical execution or structural-credit overclaim")
    need(all(r["result"] == "NOT EXECUTED" for r in traveler + inspections), "traveler/inspection falsely executed")
    need(all(r["state"] == "OPEN - NOT EXECUTED" for r in holds), "hold falsely closed")
    for row in parts:
        source = ROOT / row["source_step_path"]
        stl = OUT / row["stl_path"]
        need(source.is_file() and sha(source) == row["source_step_sha256"], f"source STEP drift: {row['part_id']}")
        need(stl.is_file() and sha(stl) == row["stl_sha256"] and stl.stat().st_size == int(row["stl_bytes"]), f"STL hash/size drift: {row['part_id']}")
        triangle_count, mesh_bbox = parse_stl(stl)
        need(triangle_count == int(row["triangle_count"]), f"STL triangle-count drift: {row['part_id']}")
        shape = cq.importers.importStep(str(source)).val()
        need(shape is not None and shape.Volume() > 0, f"invalid STEP shape: {row['part_id']}")
        cad = shape.BoundingBox()
        cad_bbox = (cad.xlen, cad.ylen, cad.zlen)
        need(all(abs(mesh_bbox[i] - cad_bbox[i]) <= 0.31 for i in range(3)), f"STL/STEP bounds mismatch: {row['part_id']} {mesh_bbox} {cad_bbox}")
        need(all(abs(float(row[f"mesh_bbox_{axis}_mm"]) - mesh_bbox[i]) <= 1e-5 for i, axis in enumerate("xyz")), f"registered mesh bounds drift: {row['part_id']}")
        need(all(abs(float(row[f"step_bbox_{axis}_mm"]) - cad_bbox[i]) <= 1e-5 for i, axis in enumerate("xyz")), f"registered STEP bounds drift: {row['part_id']}")
    for key in ["whole_body_fit_check_executed", "fit_physically_validated", "structural_credit", "production_equivalence", "procurement_authority", "production_fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["physical_part_count"] == status["stl_count"] == 98 and status["module_count"] == 12, "status counts drift")
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
    need(root["full_scale_fit_check_part_count"] == root["full_scale_fit_check_stl_count"] == 98, "root fit-check integration missing")
    need(root["full_scale_fit_check_physically_validated"] is False and root["full_scale_fit_check_structural_use_permitted"] is False, "root authority overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "font-size:14px" in page and "Print the whole robot" in page, "guide content/legibility drift")
    need("HR30-FULL-SCALE-FIT-CHECK-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    print(f"PASS: 98 source-bound full-scale STLs cover 12 HR-30 modules; {sum(int(r['triangle_count']) for r in parts):,} triangles; zero prints, inspections, structural credit or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
