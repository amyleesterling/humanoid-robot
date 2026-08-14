"""Fail-closed checks for the HR-30 whole-body joint-load architecture."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict]:
    return list(csv.DictReader((SRC / name).open(encoding="utf-8")))


def main() -> int:
    required = {
        "joint-load-screen.csv", "joint-load-architecture.md", "joint-load-architecture-status.json",
        "joint-load-architecture-source.py", "actuator-endpoint-source-register.csv",
        "transmission-candidate-source-register.csv",
    }
    require(all((SRC / name).is_file() for name in required), "joint-load artifacts missing")
    require(all((REL / name).is_file() and sha(SRC / name) == sha(REL / name) for name in required), "source/release joint-load mismatch")
    schedule = rows("joint-axis-schedule.csv")
    load = rows("joint-load-screen.csv")
    require(len(schedule) == len(load) == 25, "joint-load screen must cover exactly 25 axes")
    require({row["axis_id"] for row in schedule} == {row["axis_id"] for row in load}, "axis set mismatch")
    sources = rows("actuator-endpoint-source-register.csv")
    require(len(sources) == 4 and all(row["manufacturer"] == "ROBOTIS" for row in sources), "actuator primary-source set mismatch")
    source_by_model = {row["model"]: row for row in sources}
    require(all("STALL TORQUE IS MOMENTARY" in row["manufacturer_caveat"] for row in sources), "stall warning missing")
    transmissions = rows("transmission-candidate-source-register.csv")
    require(len(transmissions) == 2 and {row["product_number"] for row in transmissions} == {"9400-55278", "9400-55245"}, "Gates transmission candidate source set mismatch")
    require({float(row["published_mass_kg"]) for row in transmissions} == {0.014, 0.015}, "Gates transmission published mass drift")
    require(all(row["official_url"].startswith("https://www.gates.com/") and "SELECTION REQUIRED" in row["selection_state"] for row in transmissions), "transmission source/selection boundary missing")
    for row in load:
        require(row["candidate_actuator"] in source_by_model, f"unknown actuator {row['axis_id']}")
        source = source_by_model[row["candidate_actuator"]]
        expected = float(source["published_12v_stall_torque_nm"]) * float(row["candidate_ratio"]) * float(row["assumed_transmission_efficiency"])
        require(abs(expected - float(row["effective_published_stall_endpoint_nm"])) < 2e-6, f"endpoint arithmetic drift {row['axis_id']}")
        if row["development_endpoint_screen_nm"] != "SELECTION REQUIRED" and float(row["development_endpoint_screen_nm"]) > 0:
            expected_ratio = expected / float(row["development_endpoint_screen_nm"])
            require(abs(expected_ratio - float(row["stall_endpoint_to_development_screen_ratio"])) < 0.0011, f"ratio drift {row['axis_id']}")
        require(row["authority"] == "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY", f"authority drift {row['axis_id']}")
        require(row["warning"] == WARNING, f"warning drift {row['axis_id']}")
    elbows = [row for row in load if "ELBOW" in row["axis_id"]]
    require(len(elbows) == 2 and all(row["candidate_actuator"] == "ROBOTIS XM430-W350-R" for row in elbows), "both elbows must use XM430 candidate")
    require(all("CONTINUOUS/DYNAMIC/THERMAL/PHYSICAL PROOF OPEN" in row["candidate_disposition"] for row in elbows), "elbow limitation missing")
    leg = [row for row in load if row["axis_id"].startswith(("L_HIP", "L_KNEE", "L_ANKLE", "R_HIP", "R_KNEE", "R_ANKLE"))]
    require(len(leg) == 12 and sum(row["support_case_nm"] != "N/A" for row in leg) == 10, "leg support screen population mismatch")
    require(all(row["candidate_actuator"] == "ROBOTIS XC330-T288-T" for row in load if "WRIST" in row["axis_id"]), "wrist XC330 load architecture drift")
    require(all(row["candidate_actuator"] == "ROBOTIS XM430-W350-R" for row in load if "SHOULDER_ROLL" in row["axis_id"]), "shoulder-roll XM430 load architecture drift")
    require(all(row["candidate_actuator"] == "ROBOTIS XM430-W350-R" for row in load if "ANKLE" in row["axis_id"]), "ankle XM430 load architecture drift")
    require(all(float(row["candidate_ratio"]) == 2.0 for row in load if "KNEE" in row["axis_id"]), "2.0:1 knee load architecture drift")
    status = json.loads((SRC / "joint-load-architecture-status.json").read_text(encoding="utf-8"))
    require(status["axis_count"] == 25 and status["elbow_xm430_candidate_retained"] and status["wrist_xc330_candidate_retained"] and status["ankle_xm430_reduced_candidate_retained"] and status["knee_ratio"] == 2.0, "status population mismatch")
    require(not any(status[key] for key in ("published_stall_endpoint_used_as_continuous_rating", "continuous_torque_validated", "dynamic_gait_loads_validated", "actuator_selection_released", "procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "status overclaim")
    require(sha(SRC / "joint-load-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_joint_load_architecture_p01.py"), "generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require(page.count('id="joint-loads"') == 1 and "Every axis now has a load screen" in page, "web joint-load section missing")
    package_status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(package_status.get("whole_body_joint_load_architecture_present") and package_status.get("joint_load_axis_count") == 25, "package status not updated")
    print("PASS: all 25 HR-30 axes have a source-bound whole-body static architecture screen; stall remains a momentary endpoint and all selection/motion authority remains false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
