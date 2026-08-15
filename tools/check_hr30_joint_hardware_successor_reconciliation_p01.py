"""Fail-closed checks for the HR-30 joint-hardware successor crosswalk."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "joint-hardware-successor-reconciliation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
JOINT = WHOLE / "joint-hardware-manufacturing-p0.1"
WARNING = "PRELIMINARY - JOINT-HARDWARE SUCCESSOR CANDIDATES ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_manifest(package: Path) -> None:
    listed = rows(package / "file-manifest.csv")
    actual = sorted(p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(row["path"] for row in listed) == actual, f"manifest file set drift: {package}")
    for row in listed:
        path = package / row["path"]
        need(int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"manifest hash drift: {path}")
        need(row["warning"] == WARNING, f"manifest warning drift: {path}")


def main() -> int:
    status = json.loads((OUT / "reconciliation-status.json").read_text(encoding="utf-8"))
    expected = {
        "predecessor_count": 39,
        "predecessor_authoritative_count": 0,
        "predecessor_superseded_count": 39,
        "unmapped_predecessor_count": 0,
        "successor_candidate_binding_count": 39,
        "catalogue_product_candidate_positions": 28,
        "editable_custom_direct_adapter_axes": 9,
        "editable_detailed_hand_mechanisms": 2,
        "successor_validation_open_count": 39,
        "procurement_selection_count": 0,
        "fabrication_release_count": 0,
    }
    for key, value in expected.items():
        need(status.get(key) == value, f"status drift {key}: {status.get(key)}")
    for key in ("complete_joint_hardware_manufacturing_definition", "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        need(status.get(key) is False, f"unsafe status: {key}")

    bindings = rows(OUT / "successor-manufacturing-binding.csv")
    need(len(bindings) == 39 and len({r["predecessor_part_id"] for r in bindings}) == 39, "crosswalk is not 39 unique rows")
    counts = Counter(row["successor_class"] for row in bindings)
    need(counts == Counter({"CATALOGUE PRODUCT CANDIDATE": 28, "EDITABLE CUSTOM DIRECT ADAPTER": 9, "EDITABLE DETAILED HAND MECHANISM": 2}), f"successor class drift: {counts}")
    for row in bindings:
        need(row["predecessor_authoritative"] == "NO" and row["predecessor_disposition"] == "SUPERSEDED - DO NOT FABRICATE", f"legacy predecessor authority drift: {row['predecessor_part_id']}")
        need(row["successor_candidate_geometry_or_order_code_present"] == "YES", f"missing successor candidate: {row['predecessor_part_id']}")
        need(row["successor_selected_for_procurement"] == row["successor_released_for_fabrication"] == "NO", f"unsafe release state: {row['predecessor_part_id']}")
        for rel in row["authoritative_source_artifacts"].split(";"):
            need((WHOLE / rel).is_file(), f"missing successor artifact: {rel}")

    disposition = rows(WHOLE / "transmission-closure-p0.1" / "transmission-disposition-register.csv")
    need({r["predecessor_part_id"] for r in disposition} == {r["predecessor_part_id"] for r in bindings}, "transmission/crosswalk universe mismatch")
    joint_rows = rows(JOINT / "joint-hardware-part-register.csv")
    legacy = [row for row in joint_rows if row["part_id"] in {r["predecessor_part_id"] for r in bindings}]
    need(len(legacy) == 39, "joint register predecessor coverage drift")
    need(all(row["disposition"] == "SUPERSEDED PREDECESSOR - SEE SUCCESSOR RECONCILIATION; DO NOT FABRICATE" for row in legacy), "joint register still calls a predecessor a redesign")
    need(not any("REDESIGN REQUIRED" in row["disposition"] for row in legacy), "stale redesign language remains")
    joint_status = json.loads((JOINT / "joint-hardware-manufacturing-status.json").read_text(encoding="utf-8"))
    need(joint_status["redesign_required_count"] == 0 and joint_status["predecessor_superseded_count"] == 39 and joint_status["successor_validation_open_count"] == 39, "joint status not reconciled")

    binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    need(binding["generator_sha256"] == sha(ROOT / binding["generator"]), "generator binding drift")
    for source in binding["sources"]:
        need(source["sha256"] == sha(ROOT / source["path"]), f"source binding drift: {source['path']}")

    verify_manifest(OUT)
    verify_manifest(RELEASE)
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / rel) == sha(RELEASE / rel) for rel in source_files), "source/release parity drift")

    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["joint_hardware_redesign_required_count"] == 0 and root_status["joint_hardware_predecessor_superseded_count"] == 39 and root_status["joint_hardware_successor_validation_open_count"] == 39, "root status not reconciled")
    holds_text = (WHOLE / "open-holds.csv").read_text(encoding="utf-8")
    need("39 pulley/coupler redesigns" not in holds_text and "39 incomplete pulley/coupler definitions" not in holds_text, "stale open-hold contradiction remains")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:17px/1.55", "font-size:16px", "font-size:14px", "overflow:auto", "39 / 39", WARNING):
        need(token in page, f"page token missing: {token}")
    for page_path in (WHOLE / "index.html", ROOT / "index.html"):
        page_text = page_path.read_text(encoding="utf-8")
        need("joint-hardware-successor-reconciliation-p0.1/index.html" in page_text, f"navigation missing: {page_path}")
    print("PASS: 39 legacy transmission envelopes are superseded and bound to 28 catalogue pulley positions, 9 direct-adapter axes and 2 detailed hands; 39 validations open; all authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
