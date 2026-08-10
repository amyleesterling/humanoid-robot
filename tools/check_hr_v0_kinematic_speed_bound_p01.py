#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-KIN-P0.1 / R197."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    transforms = {row["transform_id"]: row for row in csv_rows(ROOT / "cad/hr-v0/generated/coordinate-convention-p0.1/transform-register.csv")}
    controls = csv_rows(ROOT / "controls/hr-v0-kinematic-speed-bound-p0.1.csv")
    config = json.loads((ROOT / "firmware/supervisor/supervisor-config.json").read_text(encoding="utf-8"))
    source = (ROOT / "firmware/supervisor/project_button_supervisor/kinematics.py").read_text(encoding="utf-8")
    model = (ROOT / "firmware/supervisor/project_button_supervisor/model.py").read_text(encoding="utf-8")
    tests = (ROOT / "firmware/supervisor/tests/test_kinematics.py").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-kinematic-speed-bound-p0.1.md").read_text(encoding="utf-8")
    page = (ROOT / "release/hr-v0/kinematic-speed-bound-p0.1/index.html").read_text(encoding="utf-8")

    j1_j2 = float(transforms["TF-002"]["ty_mm"])
    j1_h104 = float(transforms["TF-003"]["ty_mm"])
    j2_h104 = j1_h104 - j1_j2
    need(math.isclose(j1_j2, 202.550, abs_tol=1e-9), "TF-002 J1-to-J2 geometry changed")
    need(math.isclose(j1_h104, 331.600, abs_tol=1e-9), "TF-003 J1-to-H104 geometry changed")
    need(math.isclose(j2_h104, 129.050, abs_tol=1e-9), "derived J2-to-H104 geometry changed")

    kin = config.get("kinematic_model", {})
    need(kin.get("identifier") == "HR-V0-KIN-P0.1", "kinematic identifier changed")
    need(kin.get("model_type") == "PLANAR_PARALLEL_X_AXES_CONSERVATIVE_RATE_BOUND", "model type changed")
    need(kin.get("shoulder_to_elbow_m") == 0.20255 and kin.get("elbow_to_h104_m") == 0.12905, "configuration geometry changed")
    need(kin.get("tool_reach_from_h104_m") == "SELECTION REQUIRED", "unreleased tool reach was populated")
    need(config.get("kinematic_model_hash") == "SELECTION REQUIRED", "unaccepted model hash was populated")
    need(kin.get("acceptance_evidence_hash") == "SELECTION REQUIRED", "unexecuted acceptance evidence was populated")
    need(kin.get("release_state") == "CANDIDATE-NOT-RELEASED", "kinematic model was released without evidence")

    need(len(controls) == 9, "kinematic control register must contain nine rows")
    need([row["control_id"] for row in controls] == [f"KIN-{index:03d}" for index in range(1, 10)], "kinematic control IDs changed")
    need(all(row["warning"] == WARNING for row in controls), "control-register warning changed")
    need(next(row for row in controls if row["control_id"] == "KIN-004")["value"] == "SELECTION REQUIRED", "tool selection hold is absent")
    need(next(row for row in controls if row["control_id"] == "KIN-009")["value"] == "NOT EXECUTED", "physical validation was falsely marked executed")

    for token in ("canonical_model_hash", "triangle inequality", "self.kinematic_model.selections_closed", "config.kinematic_model.validator()"):
        need(token in source + model, f"source binding token missing: {token}")
    for token in ("test_repository_candidate_fails_closed", "test_repository_supervisor_constructor_refuses_open_model", "test_triangle_inequality_rate_bound_uses_both_joint_radii", "test_hash_mismatch_fails_closed"):
        need(token in tests, f"kinematic regression missing: {token}")

    combined = doc + page
    for token in ("HR-V0-KIN-P0.1", "R197", "202.550", "129.050", "SELECTION REQUIRED", "zero functional-safety credit", WARNING):
        need(token in combined, f"controlled R197 token missing: {token}")
    need("font:16px" in page and "font-size:14px" in page, "interactive-guide text floors missing")
    need(not re.search(r"(?:font-size|font):\s*(?:1[0-3]|[0-9])px", page), "undersized CSS text declaration found")
    need('id="j1"' in page and 'id="j2"' in page and 'id="tool"' in page, "interactive calculator controls missing")

    if failures:
        raise SystemExit("HR-V0 kinematic speed-bound check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 kinematic speed-bound check passed: 202.550 mm + 129.050 mm candidate geometry; nine control rows")
    print("Tool reach and hashes remain SELECTION REQUIRED; repository constructor fails closed")
    print("Physical geometry, HIL, speed/stopping evidence and qualified review remain open")
    print(WARNING)


if __name__ == "__main__":
    main()
