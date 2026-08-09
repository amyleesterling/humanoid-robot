"""Fail-closed checks for HR-V0-K1K2-APP-P0.2."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    sources = rows(ROOT / "electrical/vendor/schneider/lc1d25bd-r117/source-manifest-p0.1.csv")
    assert [row["source_id"] for row in sources] == [f"R117-SRC-{i:03d}" for i in range(1, 6)]
    by_id = {row["source_id"]: row for row in sources}
    assert by_id["R117-SRC-001"]["document_identifier"] == "MKTED210011EN version 17.1"
    assert by_id["R117-SRC-001"]["size_bytes"] == "52595312"
    assert by_id["R117-SRC-001"]["sha256"] == "ACE31998C5091FAAC5BD15C6BE1CC272E52501161B96D3184BDBBB64F9EA8293"
    assert by_id["R117-SRC-002"]["size_bytes"] == "112580"
    assert by_id["R117-SRC-002"]["sha256"] == "333EFD8170CDFADAAFBBA19CF07518E0C379380BC4BDA85D2A9355A4DB360D63"
    assert all(row["access_date"] == "2026-08-08" for row in sources)

    inputs = rows(ROOT / "electrical/contactor/hr-v0-lc1d25bd-application-inputs-p0.2.csv")
    assert [row["input_id"] for row in inputs] == [f"KAI-{i:03d}" for i in range(1, 34)]
    values = {row["input_id"]: row for row in inputs}
    assert values["KAI-004"]["value"] == "24" and values["KAI-004"]["unit"] == "VDC"
    assert values["KAI-005"]["value"] == "5.4" and values["KAI-006"]["value"] == "0.225"
    assert values["KAI-007"]["value"] == "16..24"
    assert values["KAI-010"]["value"] == "5" and values["KAI-012"]["value"] == "50"
    assert values["KAI-013"]["value"] == "10" and values["KAI-013"]["evidence_class"] == "DERIVED_SCREEN"
    assert values["KAI-015"]["status"] == "ANALYTICAL_SCREEN_ONLY"
    required = [row for row in inputs if row["required_before_supplier_query"] == "yes"]
    assert len(required) == 18
    assert all(row["status"] in {"NOT_MEASURED", "OPEN", "NOT_EXECUTED"} for row in required)
    assert all(row["warning"] == WARNING for row in inputs)
    assert not any(row["status"] in {"CLOSED", "RELEASED", "APPROVED", "PASS"} for row in inputs)

    tests = rows(ROOT / "tests/forms/hr-v0-contactor-interruption-characterization-template-p0.1.csv")
    assert [row["test_id"] for row in tests] == [f"K1K2-T{i:02d}" for i in range(1, 13)]
    assert all(row["execution_state"] == "NOT EXECUTED" for row in tests)
    assert all(row["authorization_state"] in {"NOT_AUTHORIZED", "NOT AUTHORIZED"} for row in tests)
    assert all(not row["result"] and row["raw_evidence"] == "NONE" for row in tests)

    query = (ROOT / "docs/vendor-queries/schneider-lc1d25bd-dc-application-p0.1.md").read_text(encoding="utf-8")
    for token in ("UNSENT", "version 17.1", "critical-current", "SELECTION REQUIRED A", "No supplier contact has occurred"):
        assert token in query
    doc = (ROOT / "docs/hr-v0-contactor-application-p0.2.md").read_text(encoding="utf-8")
    for token in ("HR-V0-K1K2-APP-P0.2", "EG-013", "33-row", "50 mA / 5 mA = 10", "NOT_AUTHORIZED"):
        assert token in doc
    guide = (ROOT / "release/hr-v0/contactor-application-p0.2/index.html").read_text(encoding="utf-8")
    for token in ("UNSENT", "font:16px", "font-size:14px", "font-size:12px", "data-filter", "addEventListener", "EG-013 remains PARTIAL"):
        assert token in guide

    gates = rows(ROOT / "requirements/hr-v0-energization-gates.csv")
    eg13 = next(row for row in gates if row["gate_id"] == "EG-013")
    assert eg13["status"] == "partial"
    assert "docs/hr-v0-contactor-application-p0.2.md" in eg13["evidence_location"]
    metadata = (ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8")
    assert "HR-V0-K1K2-APP-P0.2" in metadata

    print("HR-V0 K1/K2 application P0.2 check passed: 33 controlled inputs; 18 required before UNSENT query; 12 tests unexecuted")
    print("EG-013 remains PARTIAL - no contactor application or energization release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
