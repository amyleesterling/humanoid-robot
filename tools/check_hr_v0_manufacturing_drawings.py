#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-MECH-DWG-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path

import cadquery as cq
import ezdxf
from ezdxf import bbox as dxf_bbox


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-drawing-p0.1"
DOC = ROOT / "docs" / "hr-v0-manufacturing-drawing-p0.1.md"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
EXPECTED_PARTS = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]
EXPECTED_PROFILE = {
    "MV0-C01": (4, 0, 6, 2),
    "MV0-C04": (4, 0, 6, 2),
    "MV0-C05": (4, 0, 6, 0),
    "MV0-C06": (12, 12, 6, 2),
    "MV0-C07": (12, 12, 6, 2),
}


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"a", "img"}:
            values = dict(attrs)
            target = values.get("href") if tag == "a" else values.get("src")
            if target:
                self.links.append(target)


def main() -> int:
    errors: list[str] = []
    profiles = rows("profile-entity-certificate.csv")
    bindings = rows("source-binding.csv")
    coverage = rows("drawing-control-coverage.csv")
    registrations = rows("inspection-coordinate-register.csv")
    fai = rows("first-article-drawing-map.csv")
    findings = rows("finding-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8")

    if [row.get("part_id") for row in profiles] != EXPECTED_PARTS or [row.get("part_id") for row in bindings] != EXPECTED_PARTS:
        errors.append("part sequence is not exactly C01/C04/C05/C06/C07")
    if len(coverage) != 26 or len(registrations) != 5 or len(fai) != 30 or len(findings) != 4:
        errors.append(f"unexpected counts: coverage={len(coverage)} registrations={len(registrations)} fai={len(fai)} findings={len(findings)}")

    by_part = {row["part_id"]: row for row in bindings}
    for profile in profiles:
        part_id = profile["part_id"]
        expected_lines, expected_arcs, expected_holes, expected_csk = EXPECTED_PROFILE[part_id]
        if (int(profile["dxf_profile_line_count"]), int(profile["dxf_profile_arc_count"]), int(profile["through_hole_count"]), int(profile["nominal_countersink_count"])) != (expected_lines, expected_arcs, expected_holes, expected_csk):
            errors.append(f"{part_id} profile/feature counts changed")
        if profile["step_profile_edge_count"] != profile["dxf_profile_entity_count"] or float(profile["maximum_extent_delta_mm"]) > 1e-9:
            errors.append(f"{part_id} STEP/DXF finished-profile parity failed")
        if profile.get("warning") != WARNING:
            errors.append(f"{part_id} profile warning changed")

        binding = by_part[part_id]
        step = ROOT / binding["step_path"]
        dxf_path = ROOT / binding["finished_dxf_path"]
        drawing = ROOT / binding["drawing_path"]
        for label, path, expected_hash in (("STEP", step, binding["step_sha256"]), ("DXF", dxf_path, binding["finished_dxf_sha256"]), ("drawing", drawing, binding["drawing_sha256"])):
            if not path.is_file() or digest(path) != expected_hash:
                errors.append(f"{part_id} {label} identity mismatch")
        if binding.get("quotation_authorized") != "FALSE" or binding.get("fabrication_authorized") != "FALSE" or binding.get("warning") != WARNING:
            errors.append(f"{part_id} binding release state changed")
        if step.is_file() and len(cq.importers.importStep(str(step)).val().Solids()) != 1:
            errors.append(f"{part_id} STEP is not one solid")
        if dxf_path.is_file():
            if not dxf_path.read_text(encoding="utf-8").startswith(f"999\n{WARNING}\n"):
                errors.append(f"{part_id} DXF warning comment missing")
            dxf = ezdxf.readfile(dxf_path)
            model = dxf.modelspace()
            profile_entities = list(model.query('LINE ARC[layer=="FINISHED_PROFILE_STEP_DERIVED"]'))
            if len(profile_entities) != expected_lines + expected_arcs:
                errors.append(f"{part_id} DXF finished-profile entity count changed")
            if len(list(model.query('CIRCLE[layer=="M5_COUNTERSINK_NOMINAL"]'))) != expected_csk:
                errors.append(f"{part_id} nominal countersink count changed")
            all_holes = sum(len(list(model.query(f'CIRCLE[layer=="{layer}"]'))) for layer in ("M2_5_CLEARANCE", "M5_CLEARANCE", "M8_CLEARANCE"))
            if all_holes != expected_holes:
                errors.append(f"{part_id} through-hole circle count changed")
            if list(model.query("LWPOLYLINE POLYLINE SPLINE ELLIPSE")):
                errors.append(f"{part_id} DXF contains an unapproved profile entity class")
            extents = dxf_bbox.extents(profile_entities)
            if any(not math.isclose(float(profile[key]), value, abs_tol=1e-6) for key, value in (("dxf_xmin_mm", extents.extmin.x), ("dxf_xmax_mm", extents.extmax.x), ("dxf_zmin_mm", extents.extmin.y), ("dxf_zmax_mm", extents.extmax.y))):
                errors.append(f"{part_id} DXF serialized extents changed")
        if drawing.is_file():
            drawing_text = drawing.read_text(encoding="utf-8")
            required = (WARNING, "DO NOT SCALE", "SOURCE CONTROL BINDING", "ICF-01", "PRIMARY A = +Y BROAD FACE", "NOT A RELEASED ASME Y14.5", "STATUS: NONSELECTED CANDIDATE", "font-size:14px", "font-size:16px")
            for token in required:
                if token not in drawing_text:
                    errors.append(f"{part_id} drawing omits {token!r}")
            if re.search(r"font-size:(?:[0-9]|1[0-3])(?:\.\d+)?px", drawing_text):
                errors.append(f"{part_id} drawing contains text below 14 px")

    if any(row.get("coverage_class") not in {"DRAWING_EXPLICIT", "DRAWING_EXPLICIT_NONPART_HOLD"} for row in coverage):
        errors.append("one or more source controls are not drawing-explicit")
    if sum(row.get("coverage_class") == "DRAWING_EXPLICIT_NONPART_HOLD" for row in coverage) != 1:
        errors.append("STOP-006 nonpart hold coverage count changed")
    if any(row.get("physical_execution_state") != "UNEXECUTED" or row.get("fabrication_authorized") != "FALSE" or row.get("warning") != WARNING for row in coverage):
        errors.append("control coverage is not fail closed")
    if [row.get("part_id") for row in registrations] != EXPECTED_PARTS:
        errors.append("inspection registration part sequence changed")
    if any(row.get("registration_id") != "ICF-01" or row.get("physical_execution_state") != "UNEXECUTED" or "NOT A RELEASED ASME Y14.5" not in row.get("formal_gdt_state", "") or row.get("warning") != WARNING for row in registrations):
        errors.append("ICF-01 registration is incomplete or no longer fail closed")
    if any(row.get("execution_state") != "UNEXECUTED" or row.get("acceptance_state") != "NOT REVIEWED" or row.get("next_work_authorized") != "FALSE" or row.get("warning") != WARNING for row in fai):
        errors.append("FAI map is not wholly unexecuted/not authorized")
    if any(digest(ROOT / row["candidate_drawing_path"]) != row["candidate_drawing_sha256"] or digest(ROOT / row["finished_dxf_path"]) != row["finished_dxf_sha256"] or digest(ROOT / row["candidate_step_path"]) != row["candidate_step_sha256"] for row in fai):
        errors.append("one or more FAI geometry bindings changed")
    if [row.get("priority") for row in findings] != ["MAJOR", "MAJOR", "MAJOR", "BLOCKER"] or any(row.get("status") not in {"CANDIDATE CORRECTION - REVIEW OPEN", "OPEN"} or row.get("warning") != WARNING for row in findings):
        errors.append("finding register changed or is not open")

    expected_status = {
        "part_count": 5, "drawing_count": 5, "finished_dxf_count": 5, "step_binding_count": 5,
        "source_control_count": 26, "schedule_bound_control_count": 0, "first_article_operation_count": 30,
        "inspection_registration_count": 5, "finding_count": 4, "candidate_selected": False,
        "provider_contacted": False, "upload_authorized": False, "quotation_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "motion_authorized": False, "energization_authorized": False,
    }
    for key, expected in expected_status.items():
        if status.get(key) != expected:
            errors.append(f"package status {key} != {expected}")
    if status.get("warning") != WARNING:
        errors.append("package warning changed")

    parser = LinkParser()
    parser.feed(guide)
    for target in parser.links:
        if not (OUT / target).resolve().is_file():
            errors.append(f"guide target is missing: {target}")
    if len(parser.links) != 27:
        errors.append(f"guide link/image count changed: {len(parser.links)}")
    for token in ("font:16px", "font-size:14px", "font-size:13px", "five custom parts now have one readable definition chain", "26/26", "source-binding.csv"):
        if token not in guide:
            errors.append(f"guide omits {token!r}")
    for token in ("twelve LINE plus twelve ARC", "all 26 existing source controls", "ICF-01", "not a released ASME Y14.5", "P0.7 remains controlled"):
        if token not in doc_text:
            errors.append(f"document omits {token!r}")

    if errors:
        print("HR-V0 manufacturing drawing check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 manufacturing drawing P0.1 check passed: 5 STEP/DXF/drawing bindings; C06/C07 each 12 LINE + 12 ARC; 26 drawing-explicit controls; 5 ICF-01 registrations; 30 unexecuted FAI rows")
    print("P0.8 drawing candidate is not selected; no provider, quotation, fabrication, assembly, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
