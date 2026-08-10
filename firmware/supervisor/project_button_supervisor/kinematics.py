"""Conservative HR-V0 planar tool-speed bound.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

The HR-V0 J1 and J2 axes are parallel project +X axes.  This module uses the
triangle inequality to bound speed at a selected tool point without relying on
joint-angle cancellation.  It deliberately refuses to construct a validator
until the H104-to-tool reach, model hash and physical acceptance evidence are
all configuration-bound.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Sequence

if TYPE_CHECKING:
    from .model import TrajectorySample


EXPECTED_IDENTIFIER = "HR-V0-KIN-P0.1"
EXPECTED_MODEL_TYPE = "PLANAR_PARALLEL_X_AXES_CONSERVATIVE_RATE_BOUND"
EXPECTED_SHOULDER_TO_ELBOW_M = 0.20255
EXPECTED_ELBOW_TO_H104_M = 0.12905
ACCEPTED_RELEASE_STATE = "ACCEPTED-FOR-GUARDED-HIL"


class KinematicConfigurationError(ValueError):
    """An unresolved or inconsistent kinematic selection."""


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
    )


def _selected_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def canonical_model_hash(model: Mapping[str, object]) -> str:
    """Hash the exact model block using a stable UTF-8 JSON encoding."""

    encoded = json.dumps(model, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class PlanarKinematicModel:
    identifier: str
    model_type: str
    shoulder_to_elbow_m: float | None
    elbow_to_h104_m: float | None
    tool_reach_from_h104_m: float | None
    source_frame_revision: str
    mechanical_revision: str
    release_state: str
    acceptance_evidence_hash: str
    configured_model_hash: str
    calculated_model_hash: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> "PlanarKinematicModel":
        model = raw.get("kinematic_model")
        if not isinstance(model, dict):
            raise KinematicConfigurationError("kinematic_model block is absent")
        return cls(
            identifier=str(model.get("identifier", "")),
            model_type=str(model.get("model_type", "")),
            shoulder_to_elbow_m=_selected_number(model.get("shoulder_to_elbow_m")),
            elbow_to_h104_m=_selected_number(model.get("elbow_to_h104_m")),
            tool_reach_from_h104_m=_selected_number(model.get("tool_reach_from_h104_m")),
            source_frame_revision=str(model.get("source_frame_revision", "")),
            mechanical_revision=str(model.get("mechanical_revision", "")),
            release_state=str(model.get("release_state", "")),
            acceptance_evidence_hash=str(model.get("acceptance_evidence_hash", "")),
            configured_model_hash=str(raw.get("kinematic_model_hash", "")),
            calculated_model_hash=canonical_model_hash(model),
        )

    @classmethod
    def from_json(cls, path: Path) -> "PlanarKinematicModel":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise KinematicConfigurationError("supervisor configuration is not an object")
        return cls.from_mapping(raw)

    @property
    def selections_closed(self) -> bool:
        return (
            self.identifier == EXPECTED_IDENTIFIER
            and self.model_type == EXPECTED_MODEL_TYPE
            and self.shoulder_to_elbow_m == EXPECTED_SHOULDER_TO_ELBOW_M
            and self.elbow_to_h104_m == EXPECTED_ELBOW_TO_H104_M
            and self.tool_reach_from_h104_m is not None
            and self.tool_reach_from_h104_m >= 0.0
            and self.source_frame_revision == "HR-V0-FRAME-CONV-P0.1"
            and self.mechanical_revision == "HR-V0-MECH-P0.6"
            and self.release_state == ACCEPTED_RELEASE_STATE
            and _is_sha256(self.acceptance_evidence_hash)
            and _is_sha256(self.configured_model_hash)
            and self.configured_model_hash.lower() == self.calculated_model_hash
        )

    def validator(self):
        """Return the Supervisor-compatible validator only when fully bound."""

        if not self.selections_closed:
            raise KinematicConfigurationError(
                "kinematic model remains SELECTION REQUIRED; no motion validator is available"
            )
        return self.speed_bounds

    def speed_bounds(self, samples: Sequence["TrajectorySample"]) -> Sequence[float]:
        if not self.selections_closed:
            raise KinematicConfigurationError("kinematic model is not accepted")
        assert self.shoulder_to_elbow_m is not None
        assert self.elbow_to_h104_m is not None
        assert self.tool_reach_from_h104_m is not None
        distal_radius = self.elbow_to_h104_m + self.tool_reach_from_h104_m
        shoulder_radius = self.shoulder_to_elbow_m + distal_radius
        result: list[float] = []
        for sample in samples:
            if set(sample.velocities) != {"J1", "J2", "GRIPPER"}:
                raise KinematicConfigurationError("velocity axis set must be exactly J1, J2 and GRIPPER")
            j1_deg_s = float(sample.velocities["J1"])
            j2_deg_s = float(sample.velocities["J2"])
            if not math.isfinite(j1_deg_s) or not math.isfinite(j2_deg_s):
                raise KinematicConfigurationError("joint velocity is not finite")
            j1_rad_s = math.radians(abs(j1_deg_s))
            j2_rad_s = math.radians(abs(j2_deg_s))
            result.append(j1_rad_s * shoulder_radius + j2_rad_s * distal_radius)
        return result
