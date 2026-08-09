"""Fail-closed checks for HR-V0-GND-BOND-P0.1."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    sources = rows(ROOT / "electrical/vendor/grounding-r118/source-manifest-p0.1.csv")
    assert [row["source_id"] for row in sources] == [f"R118-SRC-{i:03d}" for i in range(1, 9)]
    assert all(row["access_date"] == "2026-08-08" for row in sources)
    assert sources[0]["revision_or_date"] == "2026-04-03"
    assert sources[6]["revision_or_date"] == "2026 NEC basis effective 2026-04-24"

    nodes = rows(ROOT / "electrical/grounding/hr-v0-grounding-node-register-p0.1.csv")
    assert [row["record_id"] for row in nodes] == [f"GBN-{i:03d}" for i in range(1, 16)]
    assert all("NOT APPROVED" in row["warning"] for row in nodes)
    assert not any(row["current_state"] in {"RELEASED", "APPROVED", "CLOSED"} for row in nodes)
    by_object = {row["object_or_net"]: row for row in nodes}
    assert "18 V3 modeled terminals" in by_object["ACT_0V_PE_BONDED"]["modeled_reference"]
    assert by_object["SP1"]["current_state"] == "DNP_PROHIBITED"
    assert "41 V3 modeled terminals" in by_object["SAFETY_0V"]["modeled_reference"]
    assert "5 V3 modeled terminals" in by_object["COMPUTE_0V"]["modeled_reference"]
    assert by_object["ROBOT_FRAME"]["current_state"] == "SELECTION_REQUIRED"
    assert by_object["CABLE_SHIELD_TERM"]["current_state"] == "SELECTION_REQUIRED"

    nets = rows(ROOT / "electrical/kicad/project-button-v3/net-schedule.csv")
    counts = {row["net"]: int(row["connection_count"]) for row in nets}
    assert counts["ACT_0V_PE_BONDED"] == 18
    assert counts["SAFETY_0V"] == 41
    assert counts["COMPUTE_0V"] == 5
    assert counts["ROBOT_FRAME"] == 1
    assert counts["CABLE_SHIELD_TERM"] == 1

    holds = rows(ROOT / "electrical/grounding/hr-v0-grounding-selection-matrix-p0.1.csv")
    assert [row["hold_id"] for row in holds] == [f"GBH-{i:03d}" for i in range(1, 13)]
    assert all(row["status"] in {"OPEN", "PARTIAL"} for row in holds)
    assert not any(row["status"] in {"CLOSED", "RELEASED", "APPROVED", "PASS"} for row in holds)

    tests = rows(ROOT / "tests/forms/hr-v0-grounding-bonding-survey-template-p0.1.csv")
    assert [row["test_id"] for row in tests] == [f"GB-T{i:02d}" for i in range(1, 19)]
    assert all(row["execution_state"] == "NOT EXECUTED" for row in tests)
    assert all(row["authorization_state"] == "NOT_AUTHORIZED" for row in tests)
    assert all(not row["measured_value"] and not row["result"] and row["raw_evidence"] == "NONE" for row in tests)

    doc = (ROOT / "docs/hr-v0-grounding-bonding-closure-p0.1.md").read_text(encoding="utf-8")
    for token in ("HR-V0-GND-BOND-P0.1", "SP1", "single proposed DC 0 V/PE star point", "Do not perform insulation-resistance testing", "EG-016"):
        assert token in doc
    guide = (ROOT / "release/hr-v0/grounding-bonding-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("font:16px", "font-size:14px", "font-size:12px", "data-filter", "addEventListener", "EG-016 remains PARTIAL"):
        assert token in guide

    gates = rows(ROOT / "requirements/hr-v0-energization-gates.csv")
    eg16 = next(row for row in gates if row["gate_id"] == "EG-016")
    assert eg16["status"] == "partial"
    assert "docs/hr-v0-grounding-bonding-closure-p0.1.md" in eg16["evidence_location"]
    metadata = (ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8")
    assert "HR-V0-GND-BOND-P0.1" in metadata

    print("HR-V0 grounding/bonding P0.1 check passed: 15 nodes; 12 open/partial holds; 18 surveys unexecuted")
    print("EG-016 remains PARTIAL - no bond, shield, wiring, test, or energization release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
