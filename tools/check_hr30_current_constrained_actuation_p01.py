"""Fail-closed checks for the HR-30 current-constrained actuation package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SRC = WHOLE / "current-constrained-actuation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "current-constrained-actuation-p0.1"
GEN = ROOT / "tools" / "generate_hr30_current_constrained_actuation_p01.py"
WARNING = "PRELIMINARY - CURRENT/TORQUE ARCHITECTURE CANDIDATE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

EXPECTED_MODELS = {
    "ROBOTIS XH540-W270-R": (2.69, 929, 2.49901, 2047),
    "ROBOTIS XM540-W270-R": (2.69, 929, 2.49901, 2047),
    "ROBOTIS XM430-W350-R": (2.69, 743, 1.99867, 1193),
    "ROBOTIS XC330-T288-T": (1.0, 700, 0.7, 910),
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "README.md", "index.html", "status.json", "actuator-control-register.csv",
        "axis-current-torque-register.csv", "bus-current-budget.csv", "control-sequence.md",
        "source-register.csv", "open-holds.csv", "current-constrained-actuation-source.py", "file-manifest.csv",
    }
    source_files = {path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file()}
    need(required == source_files == release_files, "package file-set mismatch")
    for name in source_files:
        need(sha(SRC / name) == sha(REL / name), f"source/release byte mismatch {name}")
    need((SRC / "current-constrained-actuation-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(SRC / "file-manifest.csv")
    need({row["path"] for row in manifest} == source_files - {"file-manifest.csv"}, "manifest file set mismatch")
    for row in manifest:
        path = SRC / row["path"]
        need(row["sha256"] == sha(path) and int(row["bytes"]) == path.stat().st_size and row["warning"] == WARNING, f"manifest mismatch {row['path']}")

    controls = rows(SRC / "actuator-control-register.csv")
    need(len(controls) == 4 and {row["actuator_model"] for row in controls} == set(EXPECTED_MODELS), "model-family control coverage mismatch")
    for row in controls:
        unit, raw, amps, maximum = EXPECTED_MODELS[row["actuator_model"]]
        need((int(row["operating_mode_address"]), int(row["current_limit_address"]), int(row["goal_current_address"]), int(row["bus_watchdog_address"]), int(row["torque_enable_address"])) == (11, 38, 102, 98, 64), f"control-table address drift {row['actuator_model']}")
        need(abs(float(row["current_unit_ma_per_raw"]) - unit) < 1e-9 and int(row["candidate_current_limit_raw"]) == raw and abs(float(row["candidate_current_a"]) - amps) < 1e-9 and int(row["published_current_limit_max_raw"]) == maximum, f"current register arithmetic drift {row['actuator_model']}")
        need("TORQUE DISABLED" in row["write_condition"] and row["authority"].startswith("NO CONNECTION") and row["warning"] == WARNING, f"control boundary drift {row['actuator_model']}")

    axis = rows(SRC / "axis-current-torque-register.csv")
    need(len(axis) == 25 and len({row["axis_id"] for row in axis}) == 25, "25-axis current allocation incomplete")
    need(Counter(row["screen_result"] for row in axis) == Counter({"PASS": 19, "NOT APPLICABLE": 6}), "static screen result population drift")
    knees = [row for row in axis if "KNEE_PITCH" in row["axis_id"]]
    need(len(knees) == 2 and all(float(row["transmission_ratio"]) == 2.5 for row in knees), "bilateral 2.5:1 knee correction missing")
    for row in axis:
        model = next(item for item in controls if item["actuator_model"] == row["actuator_model"])
        need(int(row["current_limit_raw_candidate"]) == int(model["candidate_current_limit_raw"]) and abs(float(row["candidate_current_a"]) - float(model["candidate_current_a"])) < 1e-9, f"axis/model current mismatch {row['axis_id']}")
        expected = float(row["published_stall_torque_nm"]) * float(row["candidate_current_a"]) / float(row["published_stall_current_a"]) * float(row["transmission_ratio"]) * float(row["transmission_efficiency_assumption"])
        need(abs(expected - float(row["current_limited_linear_endpoint_nm"])) < 2e-6, f"endpoint arithmetic drift {row['axis_id']}")
        if row["screen_result"] == "PASS":
            need(float(row["current_limited_linear_endpoint_nm"]) >= float(row["development_endpoint_screen_nm"]), f"false pass {row['axis_id']}")
        need("NOT CONTINUOUS TORQUE" in row["calculation_boundary"] and row["authority"].startswith("NO CONNECTION") and row["warning"] == WARNING, f"axis authority boundary drift {row['axis_id']}")

    buses = rows(SRC / "bus-current-budget.csv")
    need(len(buses) == 8 and sum(int(row["axis_count"]) for row in buses) == 25, "eight-bus coverage mismatch")
    sums = defaultdict(float)
    counts = Counter()
    for row in axis:
        sums[row["bus_id"]] += float(row["candidate_current_a"])
        counts[row["bus_id"]] += 1
    for row in buses:
        need(int(row["axis_count"]) == counts[row["bus_id"]] and abs(float(row["simultaneous_candidate_cap_a"]) - sums[row["bus_id"]]) < 1e-6, f"bus current sum drift {row['bus_id']}")
        need(row["normal_rms_demand_a"] == row["regenerative_return_a"] == "SELECTION REQUIRED" and "NOT PDU" in row["boundary"], f"bus boundary overclaim {row['bus_id']}")
    need(abs(sum(sums.values()) - 46.67779) < 1e-6, "whole-body simultaneous cap sum drift")
    shoulders = [row for row in axis if "SHOULDER_" in row["axis_id"]]
    need(len(shoulders) == 4 and all(row["actuator_model"] == "ROBOTIS XM430-W350-R" and float(row["transmission_ratio"]) == 1.5 and row["screen_result"] == "PASS" for row in shoulders), "reduced all-XM430 shoulder current policy missing")

    status = json.loads((SRC / "status.json").read_text(encoding="utf-8"))
    need((status["axis_count"], status["bus_count"], status["model_family_count"], status["nonzero_static_screen_pass_count"], status["static_screen_not_applicable_count"]) == (25, 8, 4, 19, 6), "status count drift")
    need(status["knee_ratio"] == 2.5 and status["knee_ratio_changed_from"] == 2.0 and 3.0 < status["old_knee_required_endpoint_current_a"] < 3.1, "knee decision status drift")
    false_keys = ("published_stall_used_as_continuous_rating", "external_current_validated", "connector_thermal_validated", "branch_protection_released", "continuous_torque_validated", "current_policy_released", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority")
    need(not any(status[key] for key in false_keys), "unsupported validation or authority granted")
    holds = rows(SRC / "open-holds.csv")
    need(len(holds) == 9 and all(row["state"] == "OPEN" and row["authority"].startswith("NO CONNECTION") for row in holds), "open evidence register drift")
    need(len(rows(SRC / "source-register.csv")) == 6, "primary-source register incomplete")

    sequence = (SRC / "control-sequence.md").read_text(encoding="utf-8")
    need("fresh, bounded trajectory command" in sequence and "never creates a position, velocity or current command" in sequence and "E-stop release or reset cannot resume" in sequence, "deterministic no-motion-on-reset rule missing")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    need("font:17px/1.55" in page and "font-size:16px" in page and "font-size:14px" in page and WARNING in page, "web legibility/warning drift")
    need("Current is now allocated before motion" in page and "2.5:1" in page and "model-viewer" not in page, "web guide content drift")

    whole = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(whole["current_constrained_actuation_package_present"] and whole["current_constrained_axis_count"] == 25 and whole["current_constrained_bus_count"] == 8 and whole["knee_ratio_current_boundary_correction_present"], "whole-body integration missing")
    need(not whole["current_policy_released"] and not whole["branch_protection_released"] and not whole["motion_authority"] and not whole["energization_authority"], "whole-body authority overclaim")
    need("current-constrained-actuation-p0.1/index.html" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    need("raw 929" in (WHOLE / "README.md").read_text(encoding="utf-8"), "root README integration missing")
    print("PASS: 25 HR-30 axes have current-register candidates; the 2.5:1 knees close the static endpoint screen while all physical validation and motion authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
