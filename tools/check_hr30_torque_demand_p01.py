"""Validate the HR-30 whole-body inverse-dynamics torque-demand package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
SRC = BODY / "torque-demand-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / SRC.name
WARNING = "PRELIMINARY - INVERSE-DYNAMICS DESIGN EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"


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
        "README.md", "index.html", "inverse-dynamics-samples.csv", "axis-demand-summary.csv",
        "whole-body-axis-demand.csv", "sequence-demand-summary.csv", "source-binding.csv",
        "runtime-provenance.json", "torque-demand-status.json", "open-holds.csv",
        "torque-demand-source.py", "file-manifest.csv",
    }
    need({path.name for path in SRC.iterdir() if path.is_file()} == required, "torque-demand source file set drift")
    need({path.name for path in REL.iterdir() if path.is_file()} == required, "torque-demand release file set drift")
    for name in required:
        need(sha(SRC / name) == sha(REL / name), f"source/release mismatch {name}")
    need(sha(SRC / "torque-demand-source.py") == sha(ROOT / "tools" / "generate_hr30_torque_demand_p01.py"), "generator snapshot drift")

    bindings = rows(SRC / "source-binding.csv")
    need(len(bindings) == 6 and len({row["role"] for row in bindings}) == 6, "source binding population drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"] and row["state"] == "BOUND", f"source binding mismatch {row['role']}")

    provenance = json.loads((SRC / "runtime-provenance.json").read_text(encoding="utf-8"))
    need(provenance["mujoco_version"] == mujoco.__version__ == "3.10.0", "MuJoCo runtime drift")
    need(provenance["trajectory_interval_s"] == 0.02 and provenance["design_margin"] == 1.25, "method prescription drift")
    need(provenance["official_method_source"].startswith("https://mujoco.readthedocs.io/"), "official inverse-dynamics source missing")

    model = mujoco.MjModel.from_xml_path(str((BODY / "mujoco-dynamics-validation-p0.1" / "hr30_tether_ideal_fixture.xml").resolve()))
    need((model.nq, model.nv, model.nu, model.nmocap) == (32, 31, 25, 1), "compiled model topology drift")
    mass_summary = json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    expected_mass = float(mass_summary["active_tether_dynamics_planning_mass_kg"])
    need(abs(float(model.body_subtreemass[1]) - expected_mass) < 5e-6, "model mass drift")

    samples = rows(SRC / "inverse-dynamics-samples.csv")
    summaries = rows(SRC / "axis-demand-summary.csv")
    whole = rows(SRC / "whole-body-axis-demand.csv")
    sequences = rows(SRC / "sequence-demand-summary.csv")
    need(len(samples) == 24702 and len(summaries) == 46 and len(whole) == 23 and len(sequences) == 2, "inverse-demand evidence population drift")
    need(len({(row["sequence_id"], row["sample_index"], row["axis_id"]) for row in samples}) == len(samples), "duplicate inverse-demand sample")
    need(all(row["declared_support_contact_present"] == "TRUE" for row in samples), "declared support contact missing")
    numeric_fields = (
        "contact_enabled_inverse_torque_nm", "open_chain_inverse_torque_nm", "gravity_only_torque_nm",
        "contact_contribution_nm", "candidate_current_endpoint_nm", "published_output_stall_endpoint_nm",
        "absolute_contact_demand_ratio", "absolute_open_chain_demand_ratio", "absolute_gravity_demand_ratio",
    )
    need(all(math.isfinite(float(row[field])) for row in samples for field in numeric_fields), "nonfinite inverse-demand evidence")

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in samples:
        grouped[(row["sequence_id"], row["axis_id"])].append(row)
    summary_map = {(row["sequence_id"], row["axis_id"]): row for row in summaries}
    need(set(grouped) == set(summary_map), "axis summary key drift")
    for key, evidence in grouped.items():
        summary = summary_map[key]
        demand = np.array([abs(float(row["contact_enabled_inverse_torque_nm"])) for row in evidence])
        cap = float(summary["candidate_current_endpoint_nm"])
        need(close(float(summary["peak_contact_inverse_torque_nm"]), float(demand.max())), f"peak aggregation drift {key}")
        need(close(float(summary["p95_contact_inverse_torque_nm"]), float(np.quantile(demand, 0.95, method="linear"))), f"p95 aggregation drift {key}")
        need(close(float(summary["rms_contact_inverse_torque_nm"]), float(np.sqrt(np.mean(demand * demand)))), f"RMS aggregation drift {key}")
        need(close(float(summary["fraction_over_current_endpoint"]), float(np.mean(demand > cap))), f"endpoint fraction drift {key}")
        expected_state = "WITHIN CURRENT ENDPOINT"
        if demand.max() > float(summary["published_output_stall_endpoint_nm"]):
            expected_state = "EXCEEDS PUBLISHED OUTPUT STALL ENDPOINT"
        elif demand.max() > cap:
            expected_state = "EXCEEDS CANDIDATE CURRENT ENDPOINT"
        need(summary["endpoint_state"] == expected_state, f"endpoint disposition drift {key}")

    need({row["axis_id"] for row in whole} == {key[1] for key in grouped}, "whole-body axis envelope incomplete")
    for row in whole:
        candidates = [item for item in summaries if item["axis_id"] == row["axis_id"]]
        governing = max(candidates, key=lambda item: float(item["peak_to_current_endpoint_ratio"]))
        need(row["governing_sequence"] == governing["sequence_id"] and close(float(row["peak_to_current_endpoint_ratio"]), float(governing["peak_to_current_endpoint_ratio"])), f"governing sequence drift {row['axis_id']}")

    status = json.loads((SRC / "torque-demand-status.json").read_text(encoding="utf-8"))
    expected_gap_axes = sorted({row["axis_id"] for row in summaries if row["endpoint_state"] != "WITHIN CURRENT ENDPOINT"})
    need(status["axes_exceeding_candidate_current_endpoint"] == expected_gap_axes == ["L_HIP_PITCH", "L_HIP_ROLL", "R_HIP_PITCH", "R_HIP_ROLL"], "capacity-gap axis set drift")
    need(close(status["maximum_peak_to_current_endpoint_ratio"], max(float(row["peak_to_current_endpoint_ratio"]) for row in summaries)), "status peak ratio drift")
    need(status["all_values_finite"] and status["declared_support_contacts_present"] and not status["current_allocation_closes_inverse_demand"], "status hides inverse-demand gap")
    need(not any(status[key] for key in (
        "inverse_dynamics_establishes_continuous_capacity", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    )), "torque-demand authority overclaim")
    need(status["physical_execution_count"] == 0, "physical execution overclaim")

    holds = rows(SRC / "open-holds.csv")
    need(len(holds) == 8 and all(row["state"] == "OPEN" and row["authority"] == "BLOCKS HARDWARE MOTION AND WALKING" for row in holds), "open-hold boundary drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    need(all(token in page for token in ("How much torque does the complete gait actually ask for?", "24,702 rotary-axis samples", "1.25× sizing ratio", "region")), "interactive torque-demand guide incomplete")
    need("font:17px" in page and "body{font-size:16px}" in page and "font-size:14px" in page, "torque-demand guide violates legibility floor")
    body_page = (BODY / "index.html").read_text(encoding="utf-8")
    need(body_page.count('id="torque-demand"') == 1 and "torque-demand-p0.1/index.html" in body_page, "whole-body landing integration missing")
    package_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(package_status["whole_body_torque_demand_present"] and package_status["inverse_dynamics_axis_sample_count"] == 24702, "whole-body package status missing torque demand")
    need(not package_status["current_allocation_closes_inverse_demand"] and not package_status["continuous_actuator_capacity_validated"], "whole-body status hides capacity gap")

    manifest = rows(SRC / "file-manifest.csv")
    need(len(manifest) == len(required) - 1 and len({row["file"] for row in manifest}) == len(manifest), "package manifest population drift")
    for row in manifest:
        path = SRC / row["file"]
        need(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch {row['file']}")
    need(all(row["warning"] == WARNING for table in (samples, summaries, whole, sequences, bindings, holds, manifest) for row in table), "warning drift")

    print("PASS: 24,702 whole-body rotary-axis inverse-dynamics samples reconcile to 46 sequence-axis envelopes; four hip axes exceed candidate current endpoints, worst ratio 1.814x; 4:1 successor sizing direction recorded, continuous capacity and all authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
