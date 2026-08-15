"""Fail-closed checks for the HR-30 whole-robot assembly traveler."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "assembly-guide-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "assembly-guide-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    kits = rows("module-kit-register.csv")
    operations = rows("assembly-operation-register.csv")
    checkpoints = rows("assembly-checkpoint-register.csv")
    require(len(kits) == 12 and len({row["module_id"] for row in kits}) == 12, "twelve unique module kits required")
    require(sum(int(row["fabrication_part_count"]) for row in kits) == 98, "all 98 fabrication parts must be bound")
    require(sum(int(row["axis_count"]) for row in kits) == 25 and sum(int(row["joint_fastener_count"]) for row in kits) == 156, "axis/fastener binding incomplete")
    require(sum(int(row["installed_equipment_count"]) for row in kits) == 58 and sum(int(row["harness_assembly_count"]) for row in kits) == 14, "equipment/harness binding incomplete")
    require(len(operations) == len(checkpoints) == 72, "six operations and checkpoints per module required")
    require({row["module_id"] for row in operations} == {row["module_id"] for row in kits} == {row["module_id"] for row in checkpoints}, "module coverage mismatch")
    require(all(row["completion_evidence"] == "SIGNED PHYSICAL TRAVELER REQUIRED - NOT EXECUTED" for row in operations), "operation execution overclaim")
    require(all(row["result"] == "NOT EXECUTED" and row["blocks_next_step_if_open"] == "YES" for row in checkpoints), "checkpoint fail-closed state missing")
    for row in kits:
        require((OUT / row["fabrication_step"]).resolve().is_file() and (OUT / row["integration_reference_step"]).resolve().is_file(), f"module STEP link missing: {row['module_id']}")
        require(row["warning"] == WARNING, "kit warning drift")
    status = json.loads((OUT / "assembly-status.json").read_text(encoding="utf-8"))
    require((status["module_count"], status["fabrication_part_count"], status["axis_count"], status["joint_fastener_count"], status["installed_equipment_count"], status["harness_assembly_count"]) == (12, 98, 25, 156, 58, 14), "status counts drift")
    require(not any(status[key] for key in ("physical_execution_complete", "fabrication_released", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority")), "traveler authority overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    require("font:17px/1.55" in page and "font-size:14px" in page and "overflow:auto" in page and page.count('class="module"') == 12, "interactive guide content/legibility missing")
    require("localStorage" in page and "planning aids only" in page and "not signed inspection evidence" in page, "checkbox evidence boundary missing")
    root_page = (PACKAGE / "index.html").read_text(encoding="utf-8")
    require(root_page.count("HR30-ASSEMBLY-GUIDE-P01-START") == root_page.count("HR30-ASSEMBLY-GUIDE-P01-END") == 1 and 'id="assembly-guide"' in root_page, "root guide integration missing")
    package_status = json.loads((PACKAGE / "package-status.json").read_text(encoding="utf-8"))
    require(package_status["whole_robot_assembly_traveler_present"] and package_status["assembly_traveler_module_count"] == 12 and not package_status["assembly_authority"], "root status integration missing")
    require(sha(OUT / "assembly-guide-source.py") == sha(ROOT / "tools" / "generate_hr30_assembly_guide_p01.py"), "generator snapshot drift")
    files = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    manifest = rows("file-manifest.csv")
    require({row["path"] for row in manifest} == files - {"file-manifest.csv"}, "manifest set mismatch")
    require(all(row["warning"] == WARNING and row["sha256"] == sha(OUT / row["path"]) and int(row["bytes"]) == (OUT / row["path"]).stat().st_size for row in manifest), "manifest content mismatch")
    release_files = {path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file()}
    require(files == release_files and all(sha(OUT / name) == sha(RELEASE / name) for name in files), "source/release assembly package mismatch")
    print("PASS: HR-30 assembly traveler binds 12 modules, 98 fabricated parts including both detailed hands, 25 axes, 156 joint fasteners, 58 equipment items and 14 harness assemblies; physical execution and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
