"""Fail-closed checks for the HR-V0 gripper CAD acquisition package."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    availability = read_csv(ROOT / "cad/hr-v0/gripper-source-availability-p0.1.csv")
    if {row["source_id"] for row in availability} != {f"GSRC-{value:03d}" for value in range(1, 7)}:
        raise AssertionError("source availability register membership changed")
    by_id = {row["source_id"]: row for row in availability}
    if by_id["GSRC-002"]["observed_state"] != "BROKEN_REDIRECT":
        raise AssertionError("broken official Onshape indirection was concealed")
    if by_id["GSRC-003"]["observed_state"] != "METADATA_AVAILABLE_FILES_NOT_CONTROLLED":
        raise AssertionError("Thingiverse file-control boundary was weakened")
    if by_id["GSRC-004"]["observed_state"] != "AVAILABLE_AND_FROZEN":
        raise AssertionError("frozen GitHub source state changed")
    joined = " ".join(row["evidence_boundary"] for row in availability).lower()
    for phrase in ("no cad file", "not a native assembly", "no physical mass", "does not identify a file revision"):
        if phrase not in joined:
            raise AssertionError(f"source boundary missing: {phrase}")

    controls = read_csv(ROOT / "cad/hr-v0/gripper-datum-control-p0.1.csv")
    if {row["control_id"] for row in controls} != {f"GDC-{value:03d}" for value in range(1, 11)}:
        raise AssertionError("datum-control register membership changed")
    transform = controls[:6]
    if [row["controlled_quantity"] for row in transform] != [
        "translation X", "translation Y", "translation Z", "rotation X", "rotation Y", "rotation Z"
    ]:
        raise AssertionError("six-degree H104 transform control is incomplete")
    if any(row["nominal_value"] != "SELECTION REQUIRED" or row["tolerance"] != "SELECTION REQUIRED" for row in controls):
        raise AssertionError("unsupported gripper datum value was released")
    if any(row["status"] != "OPEN" for row in controls):
        raise AssertionError("a gripper datum control was closed without evidence")

    acquisition = read_csv(ROOT / "tests/forms/hr-v0-gripper-cad-acquisition-template.csv")
    required_parts = {
        "PALM GRIPPER left and right", "LINK ROD x2", "FLANGE BUSH x4", "CRANK ARM x1",
        "RAIL BLOCK x2", "RAIL BRACKET LEFT x1", "RAIL BRACKET RIGHT x1",
        "link5 or gripper carrier", "H104-to-carrier assembly datum", "complete gripper assembly",
    }
    if not required_parts.issubset({row["expected_item"] for row in acquisition}):
        raise AssertionError("CAD acquisition part set is incomplete")
    if any(row["record_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" for row in acquisition):
        raise AssertionError("CAD acquisition template contains apparent execution evidence")
    if any(row["received_filename"] or row["sha256"] or row["manufacturing_release_claim"] for row in acquisition):
        raise AssertionError("CAD acquisition template contains unsupported received-file claims")

    metrology = read_csv(ROOT / "tests/forms/hr-v0-gripper-datum-metrology-template.csv")
    if len(metrology) != 15:
        raise AssertionError("metrology template row count changed")
    if any(row["measurement_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" for row in metrology):
        raise AssertionError("metrology template contains apparent execution evidence")
    if any(row["measured_value"] or row["expanded_uncertainty"] for row in metrology):
        raise AssertionError("metrology template contains invented measurements")

    doc = (ROOT / "docs/hr-v0-gripper-cad-acquisition-p0.1.md").read_text(encoding="utf-8")
    for token in (
        WARNING,
        "Route A - controlled publisher files",
        "Route B - controlled received-part metrology",
        "Prepared ROBOTIS support query - not sent",
        "No email, support ticket, or supplier request has been sent",
        "GRH-001",
        "GRH-002",
        "SELECTION REQUIRED",
    ):
        if token not in doc:
            raise AssertionError(f"acquisition plan missing {token!r}")

    procedures = read_csv(ROOT / "tests/procedures/procedure-registry.csv")
    audit = [row for row in procedures if row["verification_id"] == "AUDIT-GRIP-002"]
    if len(audit) != 1 or audit[0]["linked_requirement_ids"] != "GRIP-002;MECH-005;MASS-002":
        raise AssertionError("AUDIT-GRIP-002 is missing or mislinked")
    if audit[0]["status"] != "selection_required" or audit[0]["selection_required"] != "yes":
        raise AssertionError("AUDIT-GRIP-002 fail-closed state changed")

    print("HR-V0 gripper CAD acquisition check passed: 6 source states, 10 open datum controls, zero measurements")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
