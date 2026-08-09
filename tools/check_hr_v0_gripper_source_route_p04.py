"""Fail-closed checks for HR-V0-GRIP-SRC-ROUTE-P0.4."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    routes = rows(ROOT / "references/gripper/robotis-gripper-source-route-p0.2.csv")
    assert [row["route_id"] for row in routes] == [f"GSR2-{i:03d}" for i in range(1, 11)]
    by_id = {row["route_id"]: row for row in routes}
    assert by_id["GSR2-002"]["observed_state"] == "BROKEN_LEGACY_ROUTE"
    assert by_id["GSR2-003"]["locator"].endswith("no=767")
    assert by_id["GSR2-004"]["observed_state"] == "PUBLIC_VIEW_ONLY_EXPORT_NOT_EXPOSED"
    assert by_id["GSR2-005"]["observed_state"] == "METADATA_ONLY_DOWNLOAD_REQUIRES_AUTHORIZATION"
    assert by_id["GSR2-008"]["observed_state"] == "PROGRAM_OWNER_APPROVAL_REQUIRED"
    assert by_id["GSR2-009"]["observed_state"] == "UNSENT"
    assert by_id["GSR2-010"]["observed_state"] == "ANONYMOUS_ROUTES_EXHAUSTED_NO_PAYLOAD"
    assert "no CAD payload" in by_id["GSR2-010"]["release_boundary"]

    index = rows(ROOT / "references/gripper/robotis-onshape-element-index-p0.1.csv")
    assert [row["record_id"] for row in index] == [f"ONSH-{i:03d}" for i in range(1, 7)]
    values = {row["record_id"]: row for row in index}
    assert values["ONSH-001"]["id"] == "1535c2d7f05d4986e5ab539c"
    assert values["ONSH-002"]["id"] == "72b49bd8c74a47b010391012"
    assert values["ONSH-003"]["id"] == "454b64d637f42073514486f4"
    assert values["ONSH-004"]["id"] == "NO_STANDALONE_ELEMENT_ID_OBSERVED"
    assert values["ONSH-005"]["id"] == "7beff6dfbe34475b2c29540f"
    assert "c4b57aeaa8da757bd23e6e05" in values["ONSH-005"]["microversion_or_foreign_id"]
    assert values["ONSH-006"]["id"] == "e262f4f20bc9613b1ef4f9f3"

    doc = (ROOT / "docs/hr-v0-gripper-source-route-correction-p0.4.md").read_text(encoding="utf-8")
    for token in (WARNING, "GRH-001", "GRH-002", "view-only", "No dimensions were screen-measured", "closes no energization gate"):
        assert token in doc

    query = (ROOT / "docs/vendor-queries/robotis-openmanipulator-source-request-p0.2.md").read_text(encoding="utf-8")
    for token in (WARNING, "UNSENT", "enable authorized export", "assembly mates", "No supplier contact has occurred"):
        assert token in query

    guide = (ROOT / "release/hr-v0/gripper-source-route-p0.4/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "GRH-001", "GRH-002", "font-size:16px", "font-size:14px", "font-size:12px", "data-route", "addEventListener"):
        assert token in guide
    print("HR-V0 gripper source route P0.4 check passed: current route recorded; no CAD export or release inferred")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
