#!/usr/bin/env python3
"""Validate the generated HR-30 grounding/reference candidate package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30/whole-body-p0.1/electrical/grounding-reference-architecture-p0.1"
RELEASE = ROOT / "release/hr30/whole-body-p0.1/electrical/grounding-reference-architecture-p0.1"
WARNING = "PRELIMINARY - UNBUILT GROUNDING CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    status = json.loads((OUT / "grounding-reference-status.json").read_text(encoding="utf-8"))
    expected_false = [
        "architecture_approved", "bond_hardware_selected", "qualified_review_complete",
        "connection_authority", "powered_test_authority", "motion_authority", "energization_authority",
    ]
    if any(status[key] is not False for key in expected_false):
        raise RuntimeError("authority or approval gate drift")
    if status["physical_measurements_executed"] != 0:
        raise RuntimeError("false physical measurement credit")
    if status["reference_domain_count"] != 7 or status["candidate_bond_count"] != 10:
        raise RuntimeError("controlled domain/bond count drift")
    if status["instrument_connection_case_count"] != 6 or status["fault_case_count"] != 9:
        raise RuntimeError("instrument/fault count drift")
    if not status["single_removable_dc_return_pe_bond_candidate_defined"]:
        raise RuntimeError("single proposed bond missing")
    if status["normal_dc_return_through_frame_permitted"]:
        raise RuntimeError("frame incorrectly permitted as normal-current return")

    bond_rows = rows("bond-register.csv")
    br1 = [row for row in bond_rows if row["bond_id"] == "GR-PB08"]
    if len(br1) != 1 or "SOLE INTENTIONAL" not in br1[0]["disposition"]:
        raise RuntimeError("BR1 single-bond boundary drift")
    if any(row["installed"] != "NO" or row["measured"] != "NO" for row in bond_rows):
        raise RuntimeError("false installed/measured bond credit")
    if any(row["approved"] != "NO" for row in rows("reference-domain-register.csv")):
        raise RuntimeError("false domain approval")
    if any(row["approved"] != "NO" for row in rows("instrument-connection-matrix.csv")):
        raise RuntimeError("false instrument approval")
    if any(row["result"] != "NOT EXECUTED" for row in rows("fault-case-register.csv")):
        raise RuntimeError("false fault-test result")
    if any(row["measured_value"] != "NONE" or row["result"] != "NOT EXECUTED" for row in rows("measurement-traveler.csv")):
        raise RuntimeError("false measurement result")

    source_rows = rows("primary-source-register.csv")
    if len(source_rows) != 8 or any(not row["url"].startswith("https://") for row in source_rows):
        raise RuntimeError("primary-source register drift")
    for row in rows("source-binding.csv"):
        path = ROOT / row["path"]
        if not path.is_file() or sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            raise RuntimeError(f"source binding mismatch: {row['path']}")

    manifest = rows("file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    if listed != actual:
        raise RuntimeError("manifest file-set mismatch")
    for row in manifest:
        path = OUT / row["path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            raise RuntimeError(f"manifest mismatch: {row['path']}")
        if row["warning"] != WARNING:
            raise RuntimeError("manifest warning drift")
    source_files = {path.relative_to(OUT).as_posix(): sha(path) for path in OUT.rglob("*") if path.is_file()}
    release_files = {path.relative_to(RELEASE).as_posix(): sha(path) for path in RELEASE.rglob("*") if path.is_file()}
    if source_files != release_files:
        raise RuntimeError("source/release parity mismatch")

    html_text = (OUT / "index.html").read_text(encoding="utf-8")
    svg_text = (OUT / "grounding-reference-topology.svg").read_text(encoding="utf-8")
    if "font:17px" not in html_text or "font-size:16px" not in html_text:
        raise RuntimeError("web typography floor drift")
    if "font-size:16px" not in svg_text or "BR1" not in svg_text:
        raise RuntimeError("diagram legibility/topology drift")
    if WARNING not in html_text or WARNING not in (OUT / "README.md").read_text(encoding="utf-8"):
        raise RuntimeError("warning missing")
    print("PASS: HR-30 grounding/reference candidate is synchronized, legible and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
