#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-FRAME-CONV-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

from hr_v0_r213_compat import r213_allows_historical_source_hash


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "coordinate-convention-p0.1"
WEB = ROOT / "release" / "hr-v0" / "coordinate-convention-p0.1" / "index.html"
FORM = ROOT / "tests" / "forms" / "hr-v0-coordinate-calibration-template-p0.1.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise AssertionError(message)


def determinant3(matrix: list[list[float]]) -> float:
    a = matrix
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def main() -> int:
    try:
        summary = json.loads((OUT / "coordinate-convention-summary.json").read_text(encoding="utf-8"))
        frames = rows(OUT / "frame-register.csv")
        transforms = rows(OUT / "transform-register.csv")
        joints = rows(OUT / "joint-sign-register.csv")
        mapping = rows(OUT / "legacy-layout-mapping.csv")
        mirror = rows(OUT / "mirroring-register.csv")
        holds = rows(OUT / "coordinate-convention-holds.csv")
        sources = rows(OUT / "source-register.csv")
        calibration = rows(FORM)
        page = WEB.read_text(encoding="utf-8")
        svg = (OUT / "HR-V0_coordinate-sign-convention.svg").read_text(encoding="utf-8")

        if summary["identifier"] != "HR-V0-FRAME-CONV-P0.1":
            fail("identifier changed")
        if summary["a0_axes"] != {"x": "right", "y": "front", "z": "up"}:
            fail("A0 basis changed")
        if summary["j1_origin_a0_mm"] != [-210.0, 81.025, 500.0]:
            fail("J1/A0 transform changed")
        if summary["j2_origin_j1_mm"] != [0.0, 202.55, 0.0] or summary["g1_origin_j1_mm"] != [0.0, 331.6, 0.0]:
            fail("arm datum chain changed")
        if summary["j1_limits_deg"] != [-20.0, 70.0] or summary["j2_limits_deg"] != [15.0, 115.0] or summary["gripper_limits_mm"] != [20.0, 75.0]:
            fail("control limits changed")
        if any(summary[key] for key in ("raw_calibration_closed", "physical_datum_closed", "motion_authorized", "energization_authorized", "functional_safety_credit")):
            fail("an authority or physical closure flag became true")

        if len(frames) != 6 or len(transforms) != 4 or len(joints) != 3 or len(mapping) != 4 or len(mirror) != 2 or len(holds) != 10:
            fail("controlled row count changed")
        by_frame = {row["frame_id"]: row for row in frames}
        for frame_id in ("A0_BASE_CENTER", "J1_LOCAL", "J2_ZERO", "G1_H104_ZERO", "G0_RH"):
            if by_frame[frame_id]["handedness"] != "RIGHT_HANDED":
                fail(f"{frame_id} is no longer right-handed")
        legacy = by_frame["G0_LEGACY_LAYOUT"]
        if "NOT A KINEMATIC FRAME" not in legacy["handedness"] or "prohibited" not in legacy["status"].lower():
            fail("legacy guard-layout boundary weakened")

        for transform in transforms:
            matrix = json.loads(transform["matrix_4x4_row_major"])
            if not math.isclose(determinant3([row[:3] for row in matrix[:3]]), 1.0, abs_tol=1e-9):
                fail(f"{transform['transform_id']} is not a proper rotation")
        tf = {row["transform_id"]: row for row in transforms}
        if [tf["TF-001"][key] for key in ("tx_mm", "ty_mm", "tz_mm")] != ["-210.000", "81.025", "500.000"]:
            fail("TF-001 changed")
        if tf["TF-002"]["ty_mm"] != "202.550" or tf["TF-003"]["ty_mm"] != "331.600" or tf["TF-003"]["rx_deg"] != "180.000":
            fail("joint/gripper transform changed")

        by_joint = {row["axis_id"]: row for row in joints}
        if set(by_joint) != {"J1", "J2", "GRIPPER"}:
            fail("axis set changed")
        if any("RECEIVED CALIBRATION REQUIRED" not in row["raw_to_engineering"] for row in joints):
            fail("raw calibration hold weakened")
        if "+Y toward +Z" not in by_joint["J1"]["positive_rule"] or "+Y toward local +Z" not in by_joint["J2"]["positive_rule"]:
            fail("positive joint rule changed")
        if "outside the 15 deg command minimum" not in by_joint["J2"]["zero_definition"]:
            fail("J2 geometric-zero boundary lost")
        if "mesh distance is not jaw opening" not in by_joint["GRIPPER"]["raw_to_engineering"]:
            fail("gripper opening warning lost")

        if mapping[-1]["equation"] != "PROHIBITED" or "use A0 or G0_RH" not in mapping[-1]["state"]:
            fail("legacy orientation prohibition lost")
        if mirror[0]["state"] != "NOT APPLICABLE TO HR-V0" or "NOT INHERITED" not in mirror[1]["state"]:
            fail("mirroring boundary changed")

        if len(calibration) != 6 or any(row["result"] != "NOT EXECUTED" for row in calibration):
            fail("calibration form is not blank/unexecuted")
        evidence_fields = ("received_model_number", "received_firmware_version", "measured_engineering_value", "measured_raw_value", "raw_direction_result", "instrument_id", "uncertainty", "witness", "evidence_uri")
        if any(row[field] for row in calibration for field in evidence_fields):
            fail("calibration form contains invented evidence")
        if any(row["state"] not in {"OPEN", "OPEN - POWERED TEST NOT AUTHORIZED", "OPEN - HR-30 STAGE"} for row in holds):
            fail("a coordinate-convention hold is not open")

        expected_source_paths = {
            "cad/hr-v0/generated/arm-architecture-p0.7/transform-schedule.csv",
            "cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json",
            "cad/hr-v0/generated/assembly/mechanical-release-summary.json",
            "cad/hr-v0/mechanical-release-data.csv",
            "firmware/supervisor/actuator-config.json",
            "firmware/supervisor/supervisor-config.json",
            "cad/hr-v0/guard-receiver-p0.2/guard-receiver-summary.json",
        }
        if {row["path"] for row in sources} != expected_source_paths:
            fail("source set changed")
        for row in sources:
            path = ROOT / row["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"] and not r213_allows_historical_source_hash(ROOT, row["path"]):
                fail(f"source hash mismatch: {row['path']}")

        arm_transforms = {row["item"]: row for row in rows(ROOT / "cad/hr-v0/generated/arm-architecture-p0.7/transform-schedule.csv")}
        if [arm_transforms["J1 local frame"][key] for key in ("tx_mm", "ty_mm", "tz_mm")] != ["-210.0", "81.025", "500.0"]:
            fail("controlled P0.7 J1/A0 source transform changed")
        if arm_transforms["J2 joint package and S102"]["ty_mm"] != "202.55":
            fail("controlled P0.7 J2 source origin changed")
        if arm_transforms["G1 H104 frame"]["ty_mm"] != "331.6" or arm_transforms["G1 H104 frame"]["rx_deg"] != "180":
            fail("controlled P0.7 H104 source transform changed")
        arm_summary = json.loads((ROOT / "cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json").read_text(encoding="utf-8"))
        geometry = arm_summary["candidate_geometry_mm"]
        if geometry["j1_to_j2_axis"] != 202.55 or geometry["j2_to_g1_frame_origin"] != 129.05:
            fail("P0.7 geometry chain no longer matches R140")
        registration = arm_summary["actuator_axis_registration"]
        if registration["joint_output_axis"] != [-1, 0, 0] or arm_summary["axis_parallelism_math"]["j1_direction"] != [1, 0, 0]:
            fail("P0.7 actuator/project axis registration changed")
        guard = json.loads((ROOT / "cad/hr-v0/guard-receiver-p0.2/guard-receiver-summary.json").read_text(encoding="utf-8"))
        if guard["coordinate_system"] != {"origin": "G0 vertical projection of J1 on bench", "x": "depth", "y": "width", "z": "height above bench"}:
            fail("legacy guard-layout input changed; mapping needs disposition")

        actuator = json.loads((ROOT / "firmware/supervisor/actuator-config.json").read_text(encoding="utf-8"))
        binding = actuator["mechanical_limit_binding"]
        if binding["arm_architecture_revision"] != "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE" or binding.get("kinematic_basis_revision") != "HR-V0-ARM-ARCH-P0.7":
            fail("firmware no longer binds the controlled arm architecture")
        for axis in ("J1", "J2", "GRIPPER"):
            record = actuator["actuators"][axis]
            if record["direction"] != "RECEIVED CALIBRATION REQUIRED" or record["position_zero_raw"] != "RECEIVED CALIBRATION REQUIRED":
                fail(f"{axis} fail-closed calibration fields changed")

        for token in (WARNING, "HR-V0-FRAME-CONV-P0.1", "font:16px", "min=\"-20\"", "max=\"115\"", "Raw sign", "G0_LEGACY_LAYOUT", "HR-30"):
            if token not in page:
                fail(f"interactive guide missing {token}")
        if "font-size:18px" not in svg or WARNING not in svg or "+X right" not in svg or "+Y front" not in svg:
            fail("static diagram legibility/convention changed")
        document = (ROOT / "docs/hr-v0-coordinate-sign-convention-p0.1.md").read_text(encoding="utf-8")
        if "determinant `-1`" not in document or "No actuator direction may be synthesized" not in document or WARNING not in document:
            fail("controlled narrative lost a legacy-axis, mirroring, or release boundary")
        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        mechanical = next(item for item in candidate["current_products"] if item["domain"] == "mechanical")
        if mechanical.get("coordinate_convention") != "HR-V0-FRAME-CONV-P0.1":
            fail("release candidate does not bind the coordinate convention")

        print("HR-V0-FRAME-CONV-P0.1 PASS")
        print("  6 frames / 4 proper transforms / 3 axes / 4 legacy mappings / 10 open holds")
        print("  A0/J1/J2 signs and zeros controlled; raw polarity/calibration and all motion authority remain open")
        return 0
    except Exception as exc:
        print(f"HR-V0-FRAME-CONV-P0.1 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
