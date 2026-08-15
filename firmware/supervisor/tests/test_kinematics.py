from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path


SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor import (  # noqa: E402
    KinematicConfigurationError,
    PlanarKinematicModel,
    TrajectorySample,
    canonical_model_hash,
)


def accepted_model() -> PlanarKinematicModel:
    block = {
        "identifier": "HR-V0-KIN-P0.1",
        "model_type": "PLANAR_PARALLEL_X_AXES_CONSERVATIVE_RATE_BOUND",
        "shoulder_to_elbow_m": 0.20255,
        "elbow_to_h104_m": 0.12905,
        "tool_reach_from_h104_m": 0.100,
        "source_frame_revision": "HR-V0-FRAME-CONV-P0.1",
        "mechanical_revision": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "release_state": "ACCEPTED-FOR-GUARDED-HIL",
        "acceptance_evidence_hash": "A" * 64,
    }
    return PlanarKinematicModel(
        identifier=block["identifier"],
        model_type=block["model_type"],
        shoulder_to_elbow_m=block["shoulder_to_elbow_m"],
        elbow_to_h104_m=block["elbow_to_h104_m"],
        tool_reach_from_h104_m=block["tool_reach_from_h104_m"],
        source_frame_revision=block["source_frame_revision"],
        mechanical_revision=block["mechanical_revision"],
        release_state=block["release_state"],
        acceptance_evidence_hash=block["acceptance_evidence_hash"],
        configured_model_hash=canonical_model_hash(block),
        calculated_model_hash=canonical_model_hash(block),
    )


def sample(j1: float, j2: float, gripper: float = 0.0) -> TrajectorySample:
    return TrajectorySample(
        offset_ms=0,
        positions={"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0},
        velocities={"J1": j1, "J2": j2, "GRIPPER": gripper},
    )


class KinematicModelTests(unittest.TestCase):
    def test_repository_candidate_fails_closed(self) -> None:
        model = PlanarKinematicModel.from_json(SUPERVISOR_ROOT / "supervisor-config.json")
        self.assertFalse(model.selections_closed)
        with self.assertRaises(KinematicConfigurationError):
            model.validator()

    def test_repository_supervisor_constructor_refuses_open_model(self) -> None:
        from project_button_supervisor import Supervisor

        with self.assertRaises(KinematicConfigurationError):
            Supervisor.from_json(SUPERVISOR_ROOT / "supervisor-config.json", "boot-1")

    def test_zero_joint_rate_has_zero_tool_speed_bound(self) -> None:
        self.assertEqual(accepted_model().speed_bounds([sample(0.0, 0.0)]), [0.0])

    def test_triangle_inequality_rate_bound_uses_both_joint_radii(self) -> None:
        model = accepted_model()
        result = model.speed_bounds([sample(30.0, 30.0)])[0]
        expected = math.radians(30.0) * ((0.20255 + 0.12905 + 0.100) + (0.12905 + 0.100))
        self.assertAlmostEqual(result, expected, places=12)

    def test_rate_sign_cannot_reduce_the_bound(self) -> None:
        model = accepted_model()
        positive = model.speed_bounds([sample(10.0, 20.0)])[0]
        mixed = model.speed_bounds([sample(-10.0, 20.0)])[0]
        self.assertEqual(positive, mixed)

    def test_gripper_opening_rate_does_not_translate_the_h104_tool_point(self) -> None:
        model = accepted_model()
        self.assertEqual(
            model.speed_bounds([sample(10.0, 20.0, 0.0)]),
            model.speed_bounds([sample(10.0, 20.0, 50.0)]),
        )

    def test_axis_mismatch_and_nonfinite_rate_fail_closed(self) -> None:
        model = accepted_model()
        bad_axes = TrajectorySample(0, {"J1": 0.0}, {"J1": 0.0})
        with self.assertRaises(KinematicConfigurationError):
            model.speed_bounds([bad_axes])
        with self.assertRaises(KinematicConfigurationError):
            model.speed_bounds([sample(float("nan"), 0.0)])

    def test_hash_mismatch_fails_closed(self) -> None:
        model = accepted_model()
        altered = PlanarKinematicModel(**{**model.__dict__, "configured_model_hash": "B" * 64})
        self.assertFalse(altered.selections_closed)

    def test_json_loader_recomputes_the_exact_model_hash(self) -> None:
        model = accepted_model()
        block = {
            "identifier": model.identifier,
            "model_type": model.model_type,
            "shoulder_to_elbow_m": model.shoulder_to_elbow_m,
            "elbow_to_h104_m": model.elbow_to_h104_m,
            "tool_reach_from_h104_m": model.tool_reach_from_h104_m,
            "source_frame_revision": model.source_frame_revision,
            "mechanical_revision": model.mechanical_revision,
            "release_state": model.release_state,
            "acceptance_evidence_hash": model.acceptance_evidence_hash,
        }
        payload = {"kinematic_model_hash": canonical_model_hash(block), "kinematic_model": block}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = PlanarKinematicModel.from_json(path)
        self.assertTrue(loaded.selections_closed)


if __name__ == "__main__":
    unittest.main()
