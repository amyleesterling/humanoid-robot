"""Validate HR-30 bounded MuJoCo dynamics evidence and authority limits."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
SRC = BODY / "mujoco-dynamics-validation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / SRC.name


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    required = {
        "README.md", "index.html", "hr30_tether_ideal_fixture.xml", "simulation-samples.csv",
        "simulation-preview.json",
        "axis-dynamics-register.csv", "sequence-dynamics-summary.csv", "source-binding.csv",
        "runtime-provenance.json", "dynamics-validation-status.json", "open-holds.csv",
        "dynamics-validation-source.py", "file-manifest.csv",
    }
    need({path.name for path in SRC.iterdir() if path.is_file()} == required, "dynamics package file set drift")
    need({path.name for path in REL.iterdir() if path.is_file()} == required, "release dynamics package file set drift")
    for name in required:
        need(sha(SRC / name) == sha(REL / name), f"source/release mismatch {name}")
    need(sha(SRC / "dynamics-validation-source.py") == sha(ROOT / "tools" / "generate_hr30_mujoco_dynamics_validation_p01.py"), "generator snapshot drift")

    bindings = rows(SRC / "source-binding.csv")
    need(len(bindings) == 7 and len({row["role"] for row in bindings}) == 7, "source binding population drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"] and row["state"] == "BOUND", f"source binding mismatch {row['role']}")

    provenance = json.loads((SRC / "runtime-provenance.json").read_text(encoding="utf-8"))
    need(provenance["mujoco_version"] == mujoco.__version__ == "3.10.0", "MuJoCo runtime/version drift")
    need(provenance["official_runtime_source"] == "https://pypi.org/project/mujoco/3.10.0/" and provenance["official_source_accessed"] == "2026-08-17", "official runtime provenance missing")
    need(provenance["integration_timestep_s"] == 0.002 and provenance["settle_time_s"] == 0.5, "integration prescription drift")
    need(float(provenance["simulation_wall_time_s"]) > 0.0, "simulation wall-time provenance missing")
    need("ideal six-degree-of-freedom" in provenance["fixture"], "fixture boundary missing")

    model = mujoco.MjModel.from_xml_path(str((SRC / "hr30_tether_ideal_fixture.xml").resolve()))
    need((model.nq, model.nv, model.nu, model.nkey, model.nexclude, model.nmocap) == (32, 31, 25, 12, 35, 1), "compiled MuJoCo topology drift")
    mass_summary = json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    expected_mass_kg = float(mass_summary["active_tether_dynamics_planning_mass_kg"])
    need(abs(float(model.body_subtreemass[1]) - expected_mass_kg) < 5e-6, "compiled tether mass drift")
    physical_body_ids = np.flatnonzero((np.arange(model.nbody) > 0) & (model.body_mocapid < 0))
    need(len(physical_body_ids) == 26, "physical robot body population drift")
    need(float(np.min(model.body_mass[physical_body_ids])) > 0.0 and float(np.min(model.body_inertia[physical_body_ids])) > 0.0, "physical robot body still has zero mass/inertia")
    need(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trajectory_fixture") >= 0, "ideal fixture body missing")
    need(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_EQUALITY, "ideal_6dof_trajectory_fixture") >= 0, "fixture weld missing")

    summaries = rows(SRC / "sequence-dynamics-summary.csv")
    samples = rows(SRC / "simulation-samples.csv")
    preview = json.loads((SRC / "simulation-preview.json").read_text(encoding="utf-8"))
    axes = rows(SRC / "axis-dynamics-register.csv")
    need(len(summaries) == 2 and {row["sequence_id"] for row in summaries} == {"WS-R01", "WS-L01"}, "sequence result population drift")
    need(len(samples) == 1074 and len(axes) == 50, "simulation evidence population drift")
    preview_fields = {"sequence_id", "time_s", "declared_support", "active_floor_contacts", "maximum_rotary_tracking_error_deg", "left_normal_force_n", "right_normal_force_n"}
    need(len(preview) == len(samples) and all(set(row) == preview_fields for row in preview), "interactive preview population/schema drift")
    need(all(preview[index] == {key: row[key] for key in preview_fields} for index, row in enumerate(samples)), "interactive preview differs from authoritative samples")
    need(all(float(row["integration_timestep_s"]) == 0.002 and int(row["integration_step_count"]) == 5361 for row in summaries), "sequence integration extent drift")
    need(all(int(row["logged_sample_count"]) == 537 for row in summaries), "logged sequence sample count drift")
    need(all(row["numerically_finite"] == "TRUE" for row in summaries), "nonfinite simulation result")
    need(all(row["unexpected_contact_pairs"] == "NONE" for row in samples), "unexpected contact exists in sample register")
    need(all(set(row["active_floor_contacts"].split("+")) <= {"L", "R"} for row in samples), "non-foot floor contact encoded")
    need(all(row["scope"].endswith("OR WALKING") for row in summaries), "ideal-fixture scope boundary missing")
    need(all(row["authority"] == "NO HARDWARE CONTROL OR MOTION AUTHORITY" for row in axes), "axis authority overclaim")
    need(sum(row["axis_id"].endswith("_GRIPPER") for row in axes) == 4, "bilateral prismatic numerical hold records missing")
    need(all(row["screen_state"] == "PRISMATIC FORCE CALIBRATION OPEN" for row in axes if row["axis_id"].endswith("_GRIPPER")), "gripper force calibration overclaim")

    status = json.loads((SRC / "dynamics-validation-status.json").read_text(encoding="utf-8"))
    need(status["mujoco_model_compiles"] and status["all_moving_bodies_positive_mass_inertia"] and status["numerically_finite"], "executed model status incomplete")
    need((status["sequence_count"], status["simulation_logged_sample_count"], status["axis_result_count"]) == (2, 1074, 50), "status result counts drift")
    need(status["unexpected_contact_pairs"] == [], "status hides unexpected contacts")
    need(not any(status[key] for key in (
        "free_balance_validated", "physical_restraint_validated", "continuous_actuator_capacity_validated",
        "connection_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority",
    )), "dynamics validation/authority overclaim")
    need(status["physical_execution_count"] == 0, "physical execution overclaim")

    holds = rows(SRC / "open-holds.csv")
    need(len(holds) == 8 and all(row["state"] == "OPEN" and row["authority"] == "BLOCKS HARDWARE MOTION AND WALKING" for row in holds), "open-hold boundary drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    need(all(token in page for token in ("whole robot now runs in a real physics engine", "simulation-samples.csv", "simulation-preview.json", "hr30_tether_ideal_fixture.xml", "What the ideal fixture hides")), "interactive dynamics guide incomplete")
    need("fetch('simulation-preview.json').then" in page and "const rows=await fetch" not in page, "interactive preview loader is not valid in a classic script")
    need("font:17px" in page and "body{font-size:16px}" in page and "small{font-size:14px}" in page, "web text size below human-legibility rule")
    body_page = (BODY / "index.html").read_text(encoding="utf-8")
    need(body_page.count('id="mujoco-dynamics"') == 1 and "mujoco-dynamics-validation-p0.1/index.html" in body_page, "whole-body landing page missing dynamics guide")
    package_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(package_status["mujoco_dynamics_validation_present"] and package_status["mujoco_model_compiles"] and package_status["mujoco_executed_sequence_count"] == 2, "whole-body package status missing dynamics checkpoint")
    need(not package_status["free_balance_validated"] and not package_status["walking_sequence_physically_validated"], "whole-body status overclaims walking")

    manifest = rows(SRC / "file-manifest.csv")
    need(len(manifest) == len(required) - 1 and len({row["file"] for row in manifest}) == len(manifest), "manifest population drift")
    for row in manifest:
        path = SRC / row["file"]
        need(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch {row['file']}")

    result = "PASS" if status["all_sequences_pass_bounded_ideal_fixture_screen"] else "FAIL"
    max_error = max(float(row["maximum_rotary_tracking_error_deg"]) for row in summaries)
    max_saturation = max(float(row["maximum_rotary_saturation_fraction"]) for row in summaries)
    print(f"PASS evidence integrity: MuJoCo 3.10.0 compiles the positive-inertia 9.990 kg whole body and executes 2 x 10.72 s ideal-fixture sequences; bounded tracking result {result}, max rotary error {max_error:.3f} deg, max saturation {100*max_saturation:.2f}%; free balance, physical restraint, walking and all authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
