"""Fail-closed checks for HR-V0-GRIP-CAD-ACQ-P0.2."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "cad/hr-v0/gripper-cad-source-correction-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> int:
    sources = rows(BASE / "source-status.csv")
    require({row["source_id"] for row in sources} == {f"GCS-{i:03d}" for i in range(1, 7)}, "source register membership changed")
    by_source = {row["source_id"]: row for row in sources}
    require(by_source["GCS-002"]["observed_state"] == "REDIRECT_TARGET_RECOVERED", "current ROBOTIS endpoint recovery concealed")
    require(by_source["GCS-003"]["observed_state"] == "NATIVE_WORKSPACES_VISIBLE_VIEW_ONLY", "Onshape view-only boundary changed")
    require("mutable" in by_source["GCS-003"]["evidence_boundary"].lower(), "mutable Main-workspace boundary missing")
    require(by_source["GCS-004"]["observed_state"] == "AVAILABLE_AND_FROZEN", "frozen official GitHub state changed")

    elements = rows(BASE / "onshape-element-register.csv")
    require({row["element_id"] for row in elements} == {f"GCE-{i:03d}" for i in range(1, 7)}, "Onshape element membership changed")
    require({row["displayed_tab"] for row in elements} == {"Gripper", "Gripper Base", "Gripper Bolts", "Gripper Horn", "Gripper Link", "Gripper Palm"}, "native gripper workspace set changed")
    require(len({row["url"] for row in elements}) == 6, "Onshape element URLs are not unique")
    require(all(row["document_id"] == "9442f03bd8ccac084fda9dd3" and row["workspace_id"] == "039e8dbd53e0782540ea5b0d" for row in elements), "document/workspace identity drift")
    require(all(row["release_state"] == "NO EXPORT OR FABRICATION RELEASE" for row in elements), "unsupported source release claimed")

    decisions = rows(BASE / "configuration-decision.csv")
    require(len(decisions) == 3, "configuration decision row count changed")
    by_candidate = {row["candidate"]: row for row in decisions}
    require(by_candidate["OpenMANIPULATOR-X mechanism with XM430"]["decision"] == "RETAIN ACTIVE PROPOSAL - NOT SELECTED", "active proposal state changed")
    xc = by_candidate["XC330-T288 custom mechanism"]
    require("12.0 V max" in xc["electrical_fit"] and "12.6 V" in xc["electrical_fit"], "XC330/GST voltage incompatibility screen missing")
    require(xc["decision"] == "RETAIN ALTERNATE STUDY - DO NOT CONNECT", "XC330 connection hold changed")
    require(by_candidate["No gripper selection"]["decision"] == "NO SELECTION", "gripper was selected without evidence")

    holds = rows(BASE / "hold-register.csv")
    require({row["hold_id"] for row in holds} == {f"GCH-{i:03d}" for i in range(1, 13)}, "hold register membership changed")
    require(all(row["status"] == "OPEN" for row in holds), "a gripper source hold closed without evidence")

    gates = rows(ROOT / "requirements/hr-v0-gate-evidence-supplement-r193.csv")
    require({row["gate_id"] for row in gates} == {"EG-003", "EG-005", "EG-028"}, "R193 gate set changed")
    require(all(row["state"] in {"REMAINS PARTIAL", "REMAINS OPEN"} for row in gates), "R193 claims a gate closure")

    doc = (ROOT / "docs/hr-v0-gripper-cad-source-correction-p0.2.md").read_text(encoding="utf-8")
    for token in (WARNING, "mutable workspace", "HTTP 401", "12.6 V", "No supplier was contacted", "no file was exported"):
        require(token in doc, f"document boundary missing {token!r}")

    page = (ROOT / "release/hr-v0/gripper-cad-source-p0.2/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "Native source found", "No immutable export", "XC330 rail conflict", "font:16px/1.55"):
        require(token in page, f"web guide missing {token!r}")
    require("font-size:12px" not in page and "font-size:11px" not in page, "web guide contains undersized text")

    print("HR-V0 gripper CAD source correction P0.2 check passed: 6 sources, 6 native elements, 3 decisions and 12 open holds verified")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
