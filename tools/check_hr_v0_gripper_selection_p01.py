from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    compliance = rows(ROOT / "references/gripper/hr-v0-gripper-requirement-compliance-p0.1.csv")
    decisions = rows(ROOT / "requirements/hr-v0-gripper-requirement-decision-p0.1.csv")
    document = (ROOT / "docs/hr-v0-gripper-selection-correction-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/gripper-selection-p0.1/index.html").read_text(encoding="utf-8")

    assert len(compliance) == 3
    assert {row["candidate_id"] for row in compliance} == {"GRSEL-RMX52", "GRSEL-POL3551", "GRSEL-SC3219"}
    pololu = next(row for row in compliance if row["candidate_id"] == "GRSEL-POL3551")
    assert pololu["published_or_verified_opening_mm"] == "32 internal"
    assert pololu["current_40_to_70_mm_baseline_screen"].startswith("FAIL")
    assert all("NOT SELECTED" in row["selection_state"] for row in compliance)
    assert len(decisions) == 4
    assert next(row for row in decisions if row["record_id"] == "GRC-002")["change_state"] == "NO CHANGE"
    assert next(row for row in decisions if row["record_id"] == "GRC-004")["change_state"] == "CHANGE PROPOSAL - SELECTION REQUIRED"
    assert "No HR-V0 gripper candidate is selected" in document
    assert "Fails" in document and "8 mm" in document
    assert "font:16px" in guide and "font-size:14px" in guide
    assert "NO GRIPPER SELECTED" in guide
    assert "aria-pressed" in guide and "addEventListener" in guide
    print("HR-V0-GRIP-SEL-P0.1 check passed: current 40-70 mm baseline retained; 3 candidates remain unselected")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
