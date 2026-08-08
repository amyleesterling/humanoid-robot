from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def table(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    requirements = {row["id"]: row for row in table("requirements/requirements.csv")}
    sys002 = requirements["SYS-002"]
    assert "no more than 100 g" in sys002["statement"]
    assert "between 40 mm and 70 mm inclusive" in sys002["statement"]
    assert sys002["verification_id"] == "TEST-HAND-001"

    procedures = {row["verification_id"]: row for row in table("tests/procedures/procedure-registry.csv")}
    inspect = procedures["INSPECT-OBJ-001"]
    handoff = procedures["TEST-HAND-001"]
    assert inspect["status"] == "selection_required" and inspect["selection_required"] == "yes"
    assert "including uncertainty" in inspect["acceptance_criteria"]
    assert handoff["status"] == "selection_required" and handoff["selection_required"] == "yes"
    for token in ("Exactly 100", "at least 99", "zero unsafe faults", "zero payloads escape"):
        assert token in handoff["acceptance_criteria"]

    metrology = table("tests/forms/hr-v0-controlled-object-metrology-template.csv")
    cycles = table("tests/forms/hr-v0-handoff-endurance-100-cycle-template.csv")
    summary = table("tests/forms/hr-v0-handoff-endurance-summary-template.csv")
    assert [row["record_id"] for row in metrology] == [f"OBJ-{number:03d}" for number in range(1, 13)]
    assert all(not row["actual_value"].strip() for row in metrology)
    assert [row["cycle_id"] for row in cycles] == [f"HAND-{number:03d}" for number in range(1, 101)]
    assert all(row["state"] == "NOT EXECUTED" for row in cycles)
    for row in cycles:
        assert all(not row[key].strip() for key in row if key not in {"cycle_id", "state"})
    assert len(summary) == 8 and all(row["state"] == "NOT EXECUTED" for row in summary)
    assert all(not row["actual_value"].strip() for row in summary)

    document = (ROOT / "docs/hr-v0-controlled-object-handoff-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/controlled-object-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("HR-V0-OBJ-CTRL-P0.1", "100 `NOT EXECUTED`", "No object has been selected", "does not close `SYS-002`"):
        assert token in document
    for token in ("PRELIMINARY", "NOT EXECUTED", "font:16px", "font-size:14px", "aria-live", "addEventListener"):
        assert token in guide
    assert "font-size:12px" not in guide and "overflow" in guide
    print("HR-V0-OBJ-CTRL-P0.1 check passed: SYS-002 synchronized; 12 object rows and 100 handoff rows remain unexecuted")
    print("PRELIMINARY—NOT APPROVED FOR MOTION, TESTING, OR ENERGIZATION")


if __name__ == "__main__":
    main()
