#!/usr/bin/env python3
"""Native fail-closed check for R159 carrier P0.3 and its DFM package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3"
REL = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.3"
MFG = ROOT / "electrical" / "manufacturing" / "hr-v0-dxl-protection-carrier-dfm-p0.1"
PROJECT = "hr-v0-dxl-protection-carrier-p0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def circuit_fingerprint(path: Path) -> str:
    board = pcbnew.LoadBoard(str(path))
    tracks, vias, pads, edges, zones = [], [], [], [], []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            position = item.GetPosition()
            vias.append((item.GetNetname(), position.x, position.y, item.GetWidth(pcbnew.F_Cu), item.GetDrillValue(), item.TopLayer(), item.BottomLayer()))
        else:
            start, end = item.GetStart(), item.GetEnd()
            tracks.append((item.GetNetname(), item.GetLayer(), start.x, start.y, end.x, end.y, item.GetWidth()))
    for footprint in board.GetFootprints():
        if footprint.GetReference().startswith("FD"):
            continue
        for pad in footprint.Pads():
            position, size, drill = pad.GetPosition(), pad.GetSize(), pad.GetDrillSize()
            layers = tuple(layer for layer in range(pcbnew.PCB_LAYER_ID_COUNT) if pad.GetLayerSet().Contains(layer))
            pads.append((footprint.GetReference(), pad.GetNumber(), position.x, position.y, size.x, size.y, drill.x, drill.y, int(pad.GetShape()), pad.GetNetname(), layers))
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts and isinstance(drawing, pcbnew.PCB_SHAPE):
            start, end = drawing.GetStart(), drawing.GetEnd()
            edges.append((int(drawing.GetShape()), start.x, start.y, end.x, end.y, drawing.GetWidth()))
    for zone in board.Zones():
        bounds = zone.GetBoundingBox()
        zones.append((zone.GetNetname(), zone.GetLayer(), bounds.GetX(), bounds.GetY(), bounds.GetWidth(), bounds.GetHeight(), zone.GetLocalClearance(), zone.GetMinThickness()))
    payload = {
        "tracks": sorted(tracks), "vias": sorted(vias), "pads_excluding_fiducials": sorted(pads),
        "edges": sorted(edges), "zones": sorted(zones), "copper_layers": board.GetCopperLayerCount(),
        "thickness": board.GetDesignSettings().GetBoardThickness(),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()


def main() -> int:
    failures: list[str] = []
    board = pcbnew.LoadBoard(str(OUT / f"{PROJECT}.kicad_pcb"))
    settings = board.GetDesignSettings()
    if round(pcbnew.ToMM(settings.m_SolderMaskMinWidth), 6) != 0.1:
        failures.append("native soldermask dam rule must be 0.100 mm")
    if round(pcbnew.ToMM(settings.m_MinClearance), 6) != 0.1 or round(pcbnew.ToMM(settings.m_NetSettings.GetDefaultNetclass().GetClearance()), 6) != 0.1:
        failures.append("native minimum/default clearance rules must be 0.100 mm")
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    expected_fiducials = {"FD1": (10.0, 10.0), "FD2": (90.0, 10.0), "FD3": (10.0, 50.0)}
    for ref, expected in expected_fiducials.items():
        fp = footprints.get(ref)
        if fp is None:
            failures.append(f"missing global fiducial {ref}")
            continue
        position = fp.GetPosition()
        actual = (round(pcbnew.ToMM(position.x), 6), round(pcbnew.ToMM(position.y), 6))
        pads = list(fp.Pads())
        if actual != expected or len(pads) != 1:
            failures.append(f"fiducial {ref} position/pad count mismatch")
            continue
        pad = pads[0]
        size = pad.GetSize()
        if (round(pcbnew.ToMM(size.x), 6), round(pcbnew.ToMM(size.y), 6)) != (1.0, 1.0):
            failures.append(f"fiducial {ref} copper must be 1.0 mm")
        if round(pcbnew.ToMM(pad.GetLocalSolderMaskMargin()), 6) != 0.5:
            failures.append(f"fiducial {ref} mask opening must be 2.0 mm")
        if not fp.IsBoardOnly() or not fp.IsExcludedFromBOM() or not fp.IsExcludedFromPosFiles():
            failures.append(f"fiducial {ref} must be board-only and excluded from BOM/position")

    metrics = json.loads((MFG / "board-rule-metrics.json").read_text(encoding="utf-8"))
    expected_metrics = {
        "board_width_mm": 100.0, "board_height_mm": 60.0,
        "copper_layers": 4, "footprints_total": 27, "bom_placements": 20,
        "board_only_mounting_holes": 4, "board_only_global_fiducials": 3,
        "track_segments": 69, "vias": 22, "min_track_mm": 0.18,
        "min_via_drill_mm": 0.3, "min_via_annular_ring_mm": 0.15,
        "minimum_clearance_rule_mm": 0.1, "default_clearance_rule_mm": 0.1,
        "minimum_soldermask_dam_rule_mm": 0.1, "tests_executed": 0,
    }
    for key, value in expected_metrics.items():
        if metrics.get(key) != value:
            failures.append(f"metric {key} expected {value!r}, got {metrics.get(key)!r}")
    parity = json.loads((MFG / "p0.2-p0.3-circuit-parity.json").read_text(encoding="utf-8"))
    p02_path = ROOT / parity["p0_2_board"]
    p03_path = ROOT / parity["p0_3_board"]
    p02_fingerprint = circuit_fingerprint(p02_path)
    p03_fingerprint = circuit_fingerprint(p03_path)
    if p02_fingerprint != p03_fingerprint or parity.get("circuit_geometry_parity") is not True:
        failures.append("P0.2/P0.3 circuit geometry/topology parity failed")
    if parity.get("p0_2_fingerprint_sha256") != p02_fingerprint or parity.get("p0_3_fingerprint_sha256") != p03_fingerprint:
        failures.append("P0.2/P0.3 parity record hash mismatch")

    capability = rows(MFG / "provider-capability-screen.csv")
    if len(capability) != 24 or {row["capability_id"] for row in capability} != {f"CAP-{index:03d}" for index in range(1, 25)}:
        failures.append("capability screen must contain CAP-001..CAP-024")
    if any(row["provider_selected"] != "NO" or row["upload_authorized"] != "NO" or row["warning"] != WARNING for row in capability):
        failures.append("capability screen must deny selection/upload and preserve warning")
    if not any(row["screen_result"] == "PARTIAL - AT PUBLISHED LIMIT" for row in capability):
        failures.append("capability screen must preserve the at-limit mask-dam hold")

    rfi = rows(MFG / "provider-rfi.csv")
    if len(rfi) != 24 or {row["question_id"] for row in rfi} != {f"DFM-{index:03d}" for index in range(1, 25)}:
        failures.append("provider RFI must contain DFM-001..DFM-024")
    if any(row["transmission_state"] != "NOT SENT" or row["provider_response"] != "SELECTION REQUIRED" or row["project_disposition"] != "OPEN" for row in rfi):
        failures.append("every provider question must remain unsent/unanswered/open")
    if any(row[flag] != "NO" for row in rfi for flag in ("upload_authorized", "quotation_authorized", "order_authorized")):
        failures.append("provider RFI must deny upload/quotation/order")

    fai = rows(MFG / "first-article-template.csv")
    if len(fai) != 18 or any(row["execution_state"] != "NOT EXECUTED" or row["result"] or row["article_released"] != "NO" for row in fai):
        failures.append("first-article template must contain 18 blank, unreleased checks")

    submission = rows(MFG / "submission-file-register.csv")
    if len(submission) < 20:
        failures.append("submission register unexpectedly small")
    for row in submission:
        path = ROOT / row["repository_path"]
        if not path.is_file() or digest(path) != row["sha256"] or str(path.stat().st_size) != row["size_bytes"]:
            failures.append(f"submission file/hash mismatch: {row['repository_path']}")
        if row["transmission_state"] != "NOT UPLOADED" or row["upload_authorized"] != "NO" or row["provider_import_verified"] != "NO":
            failures.append(f"submission file not fail-closed: {row['file_id']}")

    status = json.loads((MFG / "package-status.json").read_text(encoding="utf-8"))
    for flag in (
        "provider_selected", "provider_contacted", "files_uploaded", "quotation_requested", "quotation_received",
        "purchase_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized",
        "energization_authorized", "functional_safety_credit",
    ):
        if status.get(flag) is not False:
            failures.append(f"DFM status {flag} must be false")
    if status.get("physical_articles") != 0 or status.get("tests_executed") != 0 or status.get("qualified_approvals") != 0:
        failures.append("DFM status must claim zero articles/tests/approvals")

    for path in MFG.iterdir():
        if path.is_file():
            copied = REL / path.name
            if not copied.is_file() or digest(path) != digest(copied):
                failures.append(f"release DFM copy mismatch: {path.name}")
    for path in OUT.rglob("*"):
        if path.is_file():
            copied = REL / "source" / path.relative_to(OUT)
            if not copied.is_file() or digest(path) != digest(copied):
                failures.append(f"release source copy mismatch: {path.relative_to(OUT).as_posix()}")
    for path in (REL / "README.md", REL / "index.html"):
        text = path.read_text(encoding="utf-8")
        if WARNING not in text or "0 uploads" not in text.lower() and path.suffix == ".html":
            failures.append(f"{path.name} missing warning/denial language")

    manifest = {row["file"]: row["sha256"] for row in rows(REL / "file-manifest.csv")}
    current = {
        path.relative_to(REL).as_posix(): digest(path)
        for path in REL.rglob("*") if path.is_file() and path.name != "file-manifest.csv"
    }
    if manifest != current:
        failures.append("P0.3 release manifest stale")

    gates = {row["gate_id"]: row["status"] for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    for gate in ("EG-003", "EG-004", "EG-014", "EG-015", "EG-024"):
        if gates.get(gate) == "closed":
            failures.append(f"{gate} must not be closed by this inquiry package")

    if failures:
        print("HR-V0 DXL protection carrier P0.3 / DFM P0.1 FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 P0.3 / DFM P0.1 PASS: 3 fiducials, 0.100 mm mask/clearance rules, 24 capability rows, 24 unsent questions, 18 blank FAI checks, zero authority.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
