"""Fail-closed checks for HR-V0-GRIP-ACQ-P0.2."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    candidates = rows("bom/hr-v0-gripper-acquisition-candidate-p0.1.csv")
    assert {row["record_id"] for row in candidates} == {"GAC-001", "GAC-002", "GAC-003"}
    by_id = {row["record_id"]: row for row in candidates}
    assert by_id["GAC-001"]["order_code"] == "905-0023-000"
    assert by_id["GAC-002"]["order_code"] == "903-0256-300"
    assert by_id["GAC-003"]["order_code"] == "903-0240-000"
    assert by_id["GAC-002"]["status"] == "REJECTED AS SOLE SOURCE"
    assert "REQUIRED SUPPLEMENT" in by_id["GAC-003"]["project_disposition"]
    assert all("RELEASED" not in row["status"] for row in candidates)

    sources = rows("references/gripper/robotis-gripper-orderable-source-register-p0.1.csv")
    assert {row["source_id"] for row in sources} == {f"GOS-{value:03d}" for value in range(1, 6)}
    assert all(row["manufacturer"] == "ROBOTIS" and row["access_date"] == "2026-08-08" for row in sources)
    assert all(row["revision_or_date"] for row in sources)
    assert "no FR12-G101GM" in {row["source_id"]: row for row in sources}["GOS-004"]["evidence_boundary"]

    kit = rows("bom/hr-v0-gripper-kit-contents.csv")
    assert len(kit) == 20
    assert all(row["order_code"] == "905-0023-000" for row in kit)
    mechanism = {row["included_item"] for row in kit}
    for required in ("PALM GRIPPER", "LINK ROD", "FLANGE BUSH", "CRANK ARM", "RAIL BLOCK", "RAIL BRACKET LEFT", "RAIL BRACKET RIGHT"):
        assert any(required in item for item in mechanism)

    doc = (ROOT / "docs/hr-v0-gripper-acquisition-correction-p0.2.md").read_text(encoding="utf-8")
    for token in (WARNING, "rejected as the sole HR-V0 gripper-mechanism source", "SELECTION REQUIRED", "GRH-001", "GRH-002", "Commerce price, stock and weight"):
        assert token in doc

    guide = (ROOT / "release/hr-v0/gripper-acquisition-p0.2/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "FR12-G101GM", "HN12-I101", "RM-X52", "REJECTED AS SOLE SOURCE"):
        assert token in guide
    assert "font-size:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide

    print("HR-V0 gripper acquisition P0.2 check passed: 3 candidates, 5 primary-source records, sole-source substitution rejected")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
