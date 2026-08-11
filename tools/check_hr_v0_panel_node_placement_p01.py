#!/usr/bin/env python3
"""Validate the fail-closed R223 panel-node placement candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement"
OUT = ROOT / "release/hr-v0/panel-node-placement-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md", "candidate-backplate-layout.csv", "reference-placement-register.csv", "conductor-route-status.csv", "stock-allocation-screen.csv", "bom-integration.csv", "source-register.csv", "open-holds.csv", "authority-boundary.csv", "panel-layout.svg", "package-status.json", "file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        need(directory.is_dir() and {path.name for path in directory.iterdir() if path.is_file()} == expected, f"package membership mismatch: {directory}")
        need(not any(path.suffix.lower() in {".pdf", ".zip", ".7z", ".rar"} for path in directory.iterdir()), f"archive/PDF prohibited: {directory}")
        manifest = rows(directory / "file-manifest.csv")
        actual = {path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
        need({row["path"] for row in manifest} == actual, f"manifest membership mismatch: {directory}")
        for row in manifest:
            path = directory / row["path"]
            need(path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"], f"manifest mismatch: {path}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    expected = {"identifier": "HR-V0-PANEL-NODE-PLACEMENT-P0.1", "round": "R223", "layout_records": 33, "explicit_nodes": 5, "route_records": 55, "open_holds": 12, "released_cut_lengths": 0, "warning": WARNING}
    for key, value in expected.items():
        need(status.get(key) == value, f"status mismatch: {key}")
    for key in ("procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
        need(status.get(key) is False, f"{key} must remain false")

    layout = {row["reference"]: row for row in rows(OUT / "candidate-backplate-layout.csv")}
    expected_nodes = {
        "XD24": (64.0, 555.0, 28.6, 58.1), "XD0": (98.6, 555.0, 28.6, 58.1),
        "XN1": (133.2, 555.0, 5.2, 60.4), "XN2": (138.4, 555.0, 5.2, 60.4), "XN3": (143.6, 555.0, 5.2, 60.4),
    }
    for ref, values in expected_nodes.items():
        need(ref in layout, f"node missing: {ref}")
        if ref in layout:
            actual = tuple(float(layout[ref][key]) for key in ("x_mm", "y_mm", "width_mm", "height_mm"))
            need(actual == values, f"node geometry changed: {ref}")
            x, y, w, h = actual
            need(0 <= x and 0 <= y and x + w <= 533.4 and y + h <= 685.8, f"node outside backplate: {ref}")
    need(tuple(float(layout["DR5"][key]) for key in ("x_mm", "y_mm", "width_mm", "height_mm")) == (54.0, 545.0, 160.0, 7.5), "DR5 geometry changed")
    need(tuple(float(layout["WD4"][key]) for key in ("x_mm", "y_mm", "width_mm", "height_mm")) == (54.0, 625.0, 323.8, 40.0), "WD4 geometry changed")
    node_boxes = [(ref, *expected_nodes[ref]) for ref in expected_nodes]
    for i, (ref_a, ax, ay, aw, ah) in enumerate(node_boxes):
        for ref_b, bx, by, bw, bh in node_boxes[i + 1:]:
            overlap = min(ax + aw, bx + bw) - max(ax, bx) > 1e-9 and min(ay + ah, by + bh) - max(ay, by) > 1e-9
            need(not overlap, f"node envelopes overlap: {ref_a}/{ref_b}")
        need(ay + ah <= 625.0, f"node overlaps WD4: {ref_a}")

    placements = {row["reference"]: row for row in rows(OUT / "reference-placement-register.csv")}
    need(set(placements) == {"F24", "FSR1", "FSR2", "H1", "J24", "JWF1", "JWP1", "K1", "K2", "KWD1", "KWD2", "S0", "S1", "S2", "SR1", "SRA1", "XD0", "XD24", "XN1", "XN2", "XN3", "XT1"}, "placement reference set changed")
    need(all(row["cut_length_use"] == "PROHIBITED" and row["terminal_position_state"] == "SELECTION REQUIRED" for row in placements.values()), "placement register implies released terminal/cut data")
    routes = rows(OUT / "conductor-route-status.csv")
    p2p = rows(ROOT / "release/hr-v0/panel-point-to-point-p0.1/point-to-point-wire-schedule.csv")
    need(len(routes) == len(p2p) == 55 and [row["wire_id"] for row in routes] == [row["wire_id"] for row in p2p], "route/P2P membership mismatch")
    need(all(row["cut_length_mm"] == "SELECTION REQUIRED" and row["route_release"] == "NOT RELEASED" for row in routes), "route or cut length falsely released")
    need(sum(row["center_to_center_manhattan_screen_mm"] != "NOT CALCULATED" for row in routes) == status.get("routes_with_planning_screen"), "planning-screen count mismatch")

    stock = {row["stock_id"]: row for row in rows(OUT / "stock-allocation-screen.csv")}
    need(stock.get("RAIL-B", {}).get("residual_before_kerf_mm") == "86.2", "rail stock arithmetic changed")
    need(stock.get("DUCT-A", {}).get("residual_before_kerf_mm") == "20.8" and "KERF" in stock["DUCT-A"]["result"], "duct stock hold/arithmetic changed")
    integration = {row["item_id"]: row for row in rows(OUT / "bom-integration.csv")}
    need(set(integration) == {"BOM-083", "BOM-084", "BOM-085", "BOM-092", "BOM-093", "BOM-094", "BOM-095"}, "BOM integration membership changed")
    system_bom = {row["item_id"]: row for row in rows(ROOT / "bom/bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom/hr-v0-bom-closure.csv")}
    need(len(system_bom) == len(closure) == 96, "current system BOM must contain 96 covered groups after R241")
    for item in ("BOM-092", "BOM-093", "BOM-094"):
        need(closure.get(item, {}).get("closure_class") == "exact_candidate_hold" and closure[item]["allowed_action"] == "HOLD", f"{item} is not held")
    need(closure.get("BOM-095", {}).get("closure_class") == "selection_required", "BOM-095 must remain selection required")
    need(closure.get("BOM-096", {}).get("closure_class") == "exact_candidate_hold", "R241 BOM-096 must remain an exact candidate on hold")
    need(system_bom["BOM-085"]["quantity"] == "8", "DR5 end-bracket quantity not synchronized")

    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 12 and all(row["state"] == "OPEN" and row["accepted"] == "FALSE" for row in holds), "hold falsely closed")
    authority = rows(OUT / "authority-boundary.csv")
    need(len(authority) == 5 and sum(row["permitted"] == "TRUE" for row in authority) == 1, "authority boundary changed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:clamp(16px", "font-size:14px", "Five real nodes", "20.8 mm", "SELECTION REQUIRED"):
        need(token in page, f"interactive guide missing token: {token}")
    need(all(row.get("warning") == WARNING for name in ("candidate-backplate-layout.csv", "reference-placement-register.csv", "conductor-route-status.csv", "stock-allocation-screen.csv", "bom-integration.csv", "source-register.csv", "open-holds.csv", "authority-boundary.csv") for row in rows(OUT / name)), "warning missing")

    if failures:
        print("HR-V0 panel node placement P0.1: FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 panel node placement P0.1: PASS")
    print(f"33 layout records; five nodes; 55 route states; {status['routes_with_planning_screen']} planning screens; 12 holds")
    print("95 BOM groups; zero released holes, cuts, wires, physical results or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
