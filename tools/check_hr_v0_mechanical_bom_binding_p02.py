#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-MECH-BOM-BIND-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

import cadquery as cq

from hr_v0_r213_compat import r213_allows_historical_source_hash


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-bom-binding-p0.2"
BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding-p0.2.csv"
DOC = ROOT / "docs" / "hr-v0-mechanical-bom-binding-p0.2.md"
GATE = ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r213.csv"
IDENTIFIER = "HR-V0-MECH-BOM-BIND-P0.2"
ARCHITECTURE = "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
PART_IDS = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            target = dict(attrs).get("href")
            if target:
                self.targets.append(target)


def bbox(shape: cq.Shape) -> tuple[float, float, float, float, float, float]:
    box = shape.BoundingBox()
    return (box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax)


def main() -> int:
    errors: list[str] = []
    binding = rows(BINDING)
    source = {row["part_id"]: row for row in rows(ROOT / "release/hr-v0/mechanical-drawing-p0.1/source-binding.csv")}
    old = {row["part_id"]: row for row in rows(ROOT / "bom/hr-v0-mechanical-custom-part-binding.csv")}
    parity = rows(OUT / "geometry-parity.csv")
    holds = rows(OUT / "open-holds.csv")
    sources = rows(OUT / "source-hash-register.csv")
    supersession = rows(OUT / "supersession-map.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    bom = {row["item_id"]: row for row in rows(ROOT / "bom/bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom/hr-v0-bom-closure.csv")}
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    supplement = rows(GATE)

    if [row.get("part_id") for row in binding] != PART_IDS or [row.get("part_id") for row in parity] != PART_IDS:
        errors.append("part sequence is not exactly C01/C04/C05/C06/C07")
    if any(row.get("quantity_candidate") != "1" for row in binding) or sum(int(row.get("quantity_candidate", "0")) for row in binding) != 5:
        errors.append("candidate quantity is not one each / five total")
    for row in binding:
        part = row["part_id"]
        expected = source[part]
        if row.get("bom_item_id") != "BOM-027" or row.get("architecture_id") != ARCHITECTURE:
            errors.append(f"{part}: BOM/architecture identity changed")
        if row.get("configuration_state") != "CURRENT HELD DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED":
            errors.append(f"{part}: configuration state changed")
        if row.get("quotation_authorized") != "FALSE" or row.get("fabrication_authorized") != "FALSE" or row.get("warning") != WARNING:
            errors.append(f"{part}: fail-closed state weakened")
        expected_fields = {
            "step_path": expected["step_path"], "step_sha256": expected["step_sha256"],
            "dxf_path": expected["finished_dxf_path"], "dxf_sha256": expected["finished_dxf_sha256"],
            "drawing_path": expected["drawing_path"], "drawing_sha256": expected["drawing_sha256"],
        }
        for field, value in expected_fields.items():
            if row.get(field) != value:
                errors.append(f"{part}: {field} differs from R137 binding")
        for path_field, hash_field in (("step_path", "step_sha256"), ("dxf_path", "dxf_sha256"), ("drawing_path", "drawing_sha256")):
            path = ROOT / row[path_field]
            if not path.is_file() or digest(path) != row[hash_field]:
                errors.append(f"{part}: {path_field} file/hash mismatch")
        step = ROOT / row["step_path"]
        if step.is_file():
            shape = cq.importers.importStep(str(step)).val()
            if len(shape.Solids()) != 1:
                errors.append(f"{part}: STEP is not one solid")
            old_shape = cq.importers.importStep(str(ROOT / old[part]["step_path"])).val()
            if max(abs(a - b) for a, b in zip(bbox(shape), bbox(old_shape))) > 1e-6:
                errors.append(f"{part}: external bounding box differs from P0.7")

    if len(parity) != 5 or any(row.get("maximum_external_bbox_delta_mm") != "0.0" or row.get("review_state") != "INDEPENDENT AND QUALIFIED REVIEW OPEN" or row.get("warning") != WARNING for row in parity):
        errors.append("geometry parity or review boundary changed")
    if len(holds) != 12 or any(row.get("state") != "OPEN" or row.get("warning") != WARNING for row in holds):
        errors.append("twelve holds are not all open")
    if len(sources) != 8:
        errors.append("source-hash register does not contain eight records")
    for row in sources:
        path = ROOT / row["repository_path"]
        hash_matches_or_is_controlled_history = (
            path.is_file()
            and (
                digest(path) == row["sha256"]
                or r213_allows_historical_source_hash(ROOT, row["repository_path"])
            )
        )
        if not hash_matches_or_is_controlled_history or row.get("warning") != WARNING:
            errors.append(f"source identity mismatch: {row.get('repository_path')}")
    if len(supersession) != 1 or "AUDIT ONLY" not in supersession[0].get("historical_use", "") or supersession[0].get("warning") != WARNING:
        errors.append("supersession boundary changed")

    expected_status = {
        "identifier": IDENTIFIER, "controlled_custom_part_candidate": ARCHITECTURE,
        "part_count": 5, "quantity_total": 5, "geometry_identity_count": 15,
        "drawing_explicit_control_count": 26, "fai_operation_count": 30,
        "open_hold_count": 12, "maximum_external_bbox_delta_mm": 0.0,
        "current_for_qualified_design_review": True, "independent_review_complete": False,
        "qualified_review_complete": False, "provider_contacted": False,
        "quotation_authorized": False, "purchase_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False,
        "motion_authorized": False, "energization_authorized": False,
    }
    for key, expected in expected_status.items():
        if status.get(key) != expected:
            errors.append(f"package status {key} != {expected!r}")
    if status.get("warning") != WARNING:
        errors.append("package warning changed")

    item = bom.get("BOM-027", {})
    if ARCHITECTURE not in item.get("manufacturer_part_number", "") or item.get("quantity") != "5" or item.get("baseline_status") != "exact_candidate_hold" or "R213" not in item.get("selection_basis", ""):
        errors.append("BOM-027 is not synchronized to the corrected five-part candidate")
    close = closure.get("BOM-027", {})
    if close.get("closure_class") != "exact_candidate_hold" or close.get("order_code_state") != "EXACT CANDIDATE" or close.get("allowed_action") != "HOLD" or "R213" not in close.get("closure_basis", ""):
        errors.append("BOM-027 closure row is not synchronized/fail closed")

    products = release.get("current_products", [])
    for domain in ("mechanical", "bill_of_materials"):
        product = next((row for row in products if row.get("domain") == domain), {})
        supports = product.get("supporting_identifiers", [])
        if IDENTIFIER not in supports or "HR-V0-MECH-BOM-BIND-P0.1" in supports:
            errors.append(f"release candidate {domain} support identity is stale")
    if [row.get("gate_id") for row in supplement] != ["EG-003", "EG-005", "EG-006"] or any(row.get("status_after") != "partial" or row.get("warning") != WARNING for row in supplement):
        errors.append("R213 gate supplement changed")
    if any(gates[gate].get("status") != "partial" for gate in ("EG-003", "EG-005", "EG-006")):
        errors.append("an affected gate was incorrectly closed")

    parser = Links()
    parser.feed(guide)
    if len(parser.targets) != 5:
        errors.append("interactive guide link count changed")
    for target in parser.targets:
        if not (OUT / target).resolve().is_file():
            errors.append(f"interactive guide target missing: {target}")
    for token in (WARNING, "Corrected custom-part files", "26 explicit controls", "30 blank FAI", "font:clamp(16px", "font-size:14px"):
        if token not in guide:
            errors.append(f"interactive guide omits {token!r}")
    for token in (WARNING, IDENTIFIER, ARCHITECTURE, "zero external bounding-box delta", "Twelve holds remain open", "EG-003", "EG-005", "EG-006"):
        if token not in doc:
            errors.append(f"document omits {token!r}")

    if errors:
        print(f"{IDENTIFIER} FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{IDENTIFIER} PASS: five corrected STEP/DXF/drawing identities; 26 explicit controls; 30 blank FAI operations")
    print("P0.7 placement/collision basis retained at zero external-envelope delta; twelve holds open; all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
