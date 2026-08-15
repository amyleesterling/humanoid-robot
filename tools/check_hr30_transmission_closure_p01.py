"""Fail-closed checks for HR30-TRANSMISSION-CLOSURE-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "transmission-closure-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "transmission-closure-p0.1"
WARNING = "PRELIMINARY - WHOLE-BODY TRANSMISSION GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    status = json.loads((OUT / "transmission-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR30-TRANSMISSION-CLOSURE-P0.1", "identifier drift")
    need(status["predecessor_placeholder_count"] == 39 and status["predecessor_successor_mapping_count"] == 39, "39-item closure missing")
    need(status["shoulder_drive_axis_count"] == 4 and status["direct_adapter_axis_count"] == 9 and status["direct_adapter_family_count"] == 4, "axis/family counts drift")
    need(status["wrist_vendor_geometry_reconciled_to_xc330"] is True, "wrist source reconciliation missing")
    for key in ("material_fit_fasteners_capacity_validated", "physical_validation_complete", "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        need(status[key] is False, f"unsafe authority drift: {key}")

    disposition = rows(OUT / "transmission-disposition-register.csv")
    need(len(disposition) == 39 and len({row["predecessor_part_id"] for row in disposition}) == 39, "disposition coverage/uniqueness failure")
    need(all(row["placeholder_geometry_remaining_authoritative"] == "NO" and row["successor_selected_for_procurement"] == "NO" for row in disposition), "disposition boundary drift")
    need(sum("LEG" in row["axis_id"] or any(token in row["axis_id"] for token in ("HIP_", "KNEE_", "ANKLE_")) for row in disposition if "PULLEY" in row["predecessor_part_type"]) == 20, "20 leg pulley successors missing")
    need(sum("SHOULDER" in row["axis_id"] for row in disposition if "PULLEY" in row["predecessor_part_type"]) == 8, "8 shoulder pulley successors missing")
    need(sum("GRIPPER" in row["axis_id"] for row in disposition) == 2, "2 gripper successors missing")
    need(sum(row["axis_id"] in {"HEAD_PAN","HEAD_TILT","WAIST_YAW","L_ELBOW_PITCH","R_ELBOW_PITCH","L_WRIST_ROTATION","R_WRIST_ROTATION","L_HIP_YAW","R_HIP_YAW"} for row in disposition) == 9, "9 direct adapter successors missing")

    direct = rows(OUT / "direct-adapter-axis-register.csv")
    need(len(direct) == 9 and len({row["axis_id"] for row in direct}) == 9, "direct allocation incomplete")
    need({row["adapter_id"] for row in direct} == {"DA-XC330-S6-L36","DA-HN12-S10-L51","DA-HN13-S17-L43","DA-HN13-S12-L61"}, "direct family set drift")
    shoulder = rows(OUT / "shoulder-drive-register.csv")
    need(len(shoulder) == 4 and all(row["motor_pulley"] == row["output_pulley"] == "GPA20GT5090-A-P10" for row in shoulder), "shoulder pulley candidate drift")
    need(all(row["belt"] == "GBN185EV5GT-090" and row["belt_teeth"] == "37" and abs(float(row["solved_pitch_center_distance_mm"]) - 42.5) < 1e-9 and abs(float(row["pitch_length_check_mm"]) - 185.0) < 1e-9 for row in shoulder), "shoulder belt geometry drift")

    transforms = rows(WHOLE / "vendor-actuator-transform-register.csv")
    wrist = [row for row in transforms if "WRIST" in row["axis_id"]]
    need(len(wrist) == 2 and all(row["vendor_source_id"] == "ROBOTIS-XC330" for row in wrist), "wrist STEP source still contradicts XC330 allocation")

    part_register = rows(OUT / "direct-adapter-part-register.csv")
    need(len(part_register) == 4 and sum(int(row["whole_robot_quantity"]) for row in part_register) == 9, "adapter part register drift")
    for row in part_register:
        step = OUT / "parts" / f"{row['adapter_id']}.step"
        svg = OUT / "drawings" / f"{row['adapter_id']}.svg"
        need(step.stat().st_size > 10_000 and svg.stat().st_size > 1_000, f"empty adapter artifact {row['adapter_id']}")
        shape = cq.importers.importStep(str(step)).val()
        need(shape.isValid() and shape.Volume() > 1_000, f"invalid adapter STEP {row['adapter_id']}")

    for name, minimum in (("HR-30_transmission_hardware_only_candidate.step", 1_000_000), ("HR-30_transmissions_installed_candidate.step", 10_000_000), ("HR-30_transmission_hardware_only_candidate.glb", 100_000), ("HR-30_transmissions_installed_candidate.glb", 1_000_000)):
        need((OUT / name).stat().st_size > minimum, f"missing/undersized export {name}")

    manifest = rows(OUT / "file-manifest.csv")
    actual = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(len(manifest) == len(actual), "manifest count drift")
    indexed = {row["path"]: row for row in manifest}
    for path in actual:
        rel = path.relative_to(OUT).as_posix()
        need(rel in indexed and int(indexed[rel]["bytes"]) == path.stat().st_size and indexed[rel]["sha256"] == sha(path), f"manifest mismatch {rel}")
        need(indexed[rel]["warning"] == WARNING, f"warning drift {rel}")

    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    need(source_files == release_files, "source/release file set drift")
    need(all(sha(OUT / rel) == sha(RELEASE / rel) for rel in source_files), "source/release hash drift")

    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["transmission_predecessor_placeholder_successor_mapping_complete"] is True and root_status["direct_output_adapter_axis_count"] == 9, "root status not integrated")
    need(all(root_status[key] is False for key in ("procurement_authority","fabrication_authority","assembly_authority","powered_test_authority","motion_authority","energization_authority")), "root authority drift")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px/1.55" in page and "font-size:14px" in page and "39 / 39" in page, "web legibility/content drift")
    print("PASS: 39 predecessor transmissions mapped; 4 shoulder drives + 9 direct adapters + whole-body STEP/GLB verified; all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
