"""Validate the failed HR-30 4:1 hip dynamics-successor package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import mujoco


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
SRC = BODY / "dynamics-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / SRC.name
WARNING = "PRELIMINARY - NUMERICAL HIP-REDUCTION SUCCESSOR ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
HIP_AXES = {"L_HIP_PITCH", "R_HIP_PITCH", "L_HIP_ROLL", "R_HIP_ROLL"}
EXPECTED_FAIL_AXES = {
    "L_ANKLE_PITCH", "L_ANKLE_ROLL", "L_KNEE_PITCH",
    "R_ANKLE_PITCH", "R_ANKLE_ROLL", "R_KNEE_PITCH",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float, right: float, tolerance: float = 1e-6) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def main() -> int:
    required = {
        "README.md", "index.html", "hr30_tether_hip4_inverse_feedforward.xml",
        "successor-samples.csv", "axis-successor-results.csv",
        "sequence-successor-summary.csv", "hip4-transmission-scenario.csv",
        "source-binding.csv", "runtime-provenance.json", "dynamics-successor-status.json",
        "open-holds.csv", "dynamics-successor-source.py", "file-manifest.csv",
    }
    need({path.name for path in SRC.iterdir() if path.is_file()} == required, "successor source file set drift")
    need({path.name for path in REL.iterdir() if path.is_file()} == required, "successor release file set drift")
    for name in required:
        need(sha(SRC / name) == sha(REL / name), f"source/release mismatch {name}")
    need(sha(SRC / "dynamics-successor-source.py") == sha(ROOT / "tools" / "generate_hr30_dynamics_successor_p01.py"), "generator snapshot drift")

    bindings = rows(SRC / "source-binding.csv")
    need(len(bindings) == 9 and len({row["role"] for row in bindings}) == 9, "source-binding population drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"] and row["state"] == "BOUND", f"source binding mismatch {row['role']}")

    provenance = json.loads((SRC / "runtime-provenance.json").read_text(encoding="utf-8"))
    need(provenance["mujoco_version"] == mujoco.__version__ == "3.10.0", "MuJoCo runtime drift")
    need(provenance["integration_timestep_s"] == 0.002 and provenance["settle_time_s"] == 0.5, "integration prescription drift")
    need(provenance["hip_successor_ratio"] == 4.0, "successor ratio drift")
    need(provenance["thresholds"] == {
        "maximum_rotary_error_deg": 5.0,
        "maximum_gripper_error_mm": 2.0,
        "maximum_rotary_saturation_fraction": 0.1,
        "minimum_support_coverage": 0.99,
    }, "successor thresholds drift")

    model = mujoco.MjModel.from_xml_path(str((SRC / "hr30_tether_hip4_inverse_feedforward.xml").resolve()))
    need((model.nq, model.nv, model.nu, model.nmocap) == (32, 31, 25, 1), "successor compiled topology drift")
    scenario = rows(SRC / "hip4-transmission-scenario.csv")
    need(len(scenario) == 4 and {row["axis_id"] for row in scenario} == HIP_AXES, "hip scenario axis drift")
    for row in scenario:
        need(float(row["successor_ratio"]) == 4.0, f"ratio drift {row['axis_id']}")
        need(float(row["successor_peak_margin_ratio"]) > 1.0 and float(row["speed_reserve_ratio"]) > 1.0, f"hip endpoint screen drift {row['axis_id']}")
        actuator_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"M_{row['axis_id']}")
        need(actuator_id >= 0 and model.actuator_ctrllimited[actuator_id], f"hip control range missing {row['axis_id']}")
        need(close(float(model.actuator_ctrlrange[actuator_id, 1]), float(row["successor_current_endpoint_nm"])), f"compiled hip control cap drift {row['axis_id']}")

    samples = rows(SRC / "successor-samples.csv")
    axes = rows(SRC / "axis-successor-results.csv")
    summaries = rows(SRC / "sequence-successor-summary.csv")
    need(len(samples) == 1074 and len(axes) == 50 and len(summaries) == 2, "successor evidence population drift")
    need({row["sequence_id"] for row in summaries} == {"WS-L01", "WS-R01"}, "successor sequence drift")
    need(len({(row["sequence_id"], row["axis_id"]) for row in axes}) == 50, "duplicate successor axis result")
    numeric_axis_fields = (
        "control_limit", "maximum_abs_control", "maximum_abs_unclipped_command",
        "maximum_tracking_error", "rms_tracking_error", "saturation_fraction",
        "baseline_saturation_fraction", "absolute_mechanical_work_j",
    )
    need(all(math.isfinite(float(row[field])) for row in axes for field in numeric_axis_fields), "nonfinite successor axis result")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in axes:
        grouped[row["sequence_id"]].append(row)
    for summary in summaries:
        evidence = grouped[summary["sequence_id"]]
        rotary = [row for row in evidence if not row["axis_id"].endswith("_GRIPPER")]
        need(close(float(summary["maximum_rotary_saturation_fraction"]), max(float(row["saturation_fraction"]) for row in rotary)), f"sequence saturation aggregation drift {summary['sequence_id']}")
        need(summary["numerically_finite"] == "TRUE" and summary["unexpected_contact_step_count"] == "0", f"successor numerical/contact drift {summary['sequence_id']}")
        need(float(summary["declared_support_coverage_fraction"]) >= 0.99, f"support coverage drift {summary['sequence_id']}")
        need(summary["result"] == "FAIL SUCCESSOR IDEAL-FIXTURE NUMERICAL SCREEN", f"failed result hidden {summary['sequence_id']}")

    need(all(row["screen_state"] == "PASS BOUNDED NUMERICAL SCREEN" for row in axes if row["axis_id"] in HIP_AXES), "one or more revised hip axes fail")
    fail_axes = {row["axis_id"] for row in axes if row["screen_state"] == "FAIL BOUNDED NUMERICAL SCREEN"}
    need(fail_axes == EXPECTED_FAIL_AXES, "knee/ankle rejection set drift")
    need(all(float(row["saturation_fraction"]) > 0.1 for row in axes if row["screen_state"] == "FAIL BOUNDED NUMERICAL SCREEN"), "failure is not saturation-driven")

    status = json.loads((SRC / "dynamics-successor-status.json").read_text(encoding="utf-8"))
    need(status["numerically_finite"] and status["unexpected_contact_pairs"] == [], "status numerical/contact drift")
    need(not status["all_sequences_pass_bounded_successor_screen"], "status hides failed screen")
    need(status["sequence_count"] == 2 and status["simulation_logged_sample_count"] == 1074 and status["axis_result_count"] == 50, "status population drift")
    need(not any(status[key] for key in (
        "transmission_geometry_validated", "transmission_inertia_backlash_modeled",
        "continuous_actuator_capacity_validated", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    )), "successor authority overclaim")

    holds = rows(SRC / "open-holds.csv")
    need(len(holds) == 8 and all(row["state"] == "OPEN" for row in holds), "successor open-hold drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    need("does not clear the numerical screen" in page and "rejected controller-and-model configuration" in page, "failed result not presented honestly")
    need("clears the same numerical gait screen" not in page, "stale pass claim remains")
    need("font:17px" in page and "body{font-size:16px}" in page and "font-size:14px" in page, "successor guide violates legibility floor")
    body_page = (BODY / "index.html").read_text(encoding="utf-8")
    need(body_page.count('id="dynamics-successor"') == 1 and "fails the bounded gait screen" in body_page, "whole-body landing hides failed successor")
    package_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(package_status["dynamics_successor_present"] and not package_status["dynamics_successor_bounded_screen_pass"], "whole-body package status hides failed successor")
    need(not package_status["physical_hip_transmission_validated"] and not package_status["continuous_actuator_capacity_validated"], "whole-body status overclaims successor capacity")

    manifest = rows(SRC / "file-manifest.csv")
    need(len(manifest) == len(required) - 1 and len({row["file"] for row in manifest}) == len(manifest), "successor manifest population drift")
    for row in manifest:
        path = SRC / row["file"]
        need(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch {row['file']}")
    need(all(row["warning"] == WARNING for table in (samples, axes, summaries, scenario, bindings, holds, manifest) for row in table), "successor warning drift")

    print("PASS: failed 4:1 hip successor is preserved honestly; all revised hip axes pass, six unique knee/ankle axes drive 31-53% sequence saturation; no physical or walking authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
