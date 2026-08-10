#!/usr/bin/env python3
"""Fail-closed validation for the R205 Pi observation integration package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/integration/hr-v0-pi-observation-integration-p0.1"
WEB = ROOT / "release/hr-v0/pi-observation-integration-p0.1"
PANEL = ROOT / "electrical/panel/hr-v0-control-panel-p0.6"
R161 = ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def manhattan(points: list[tuple[float, float]]) -> float:
    return sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(points, points[1:]))


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    common = {
        "README.md", "panel-placement.csv", "collision-clearance-register.csv", "mounting-hole-screen.csv",
        "harness-route.csv", "harness-length-calculation.csv", "interface-parity.csv", "source-register.csv",
        "selection-holds.csv", "acceptance-matrix.csv", "package-status.json", "panel-integration.svg", "SOURCE-MANIFEST.csv",
    }
    for directory, expected in ((ENG, common), (WEB, common | {"index.html"})):
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
        need(actual == expected, f"package membership mismatch: {directory.name}: {sorted(actual ^ expected)}")
        need(not any(p.suffix.lower() in {".zip", ".7z", ".rar", ".pdf"} for p in directory.rglob("*")), f"archive/PDF found in {directory.name}")

    status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-PI-OBS-INTEGRATION-P0.1", "identifier changed")
    need(status.get("round") == "R205", "round changed")
    expected_counts = {"placement_rows": 2, "clearance_rows": 10, "mounting_hole_rows": 4, "route_node_rows": 8, "interface_rows": 11, "selection_holds": 13, "acceptance_rows": 16}
    for key, expected in expected_counts.items():
        need(status.get(key) == expected, f"status count changed: {key}")
    need(status.get("compute_nominal_centerline_mm") == 335.4, "compute route summary changed")
    need(status.get("field_nominal_centerline_mm") == 276.0, "field route summary changed")
    need(status.get("warning") == WARNING, "warning changed")
    for key, value in status.items():
        if key.endswith(("_authorized", "_released", "_approved")) or key in {
            "cut_lengths_selected", "panel_layout_superseded", "physical_article_exists", "physical_test_executed",
            "qualified_review_complete", "safety_credit", "buildable", "energization_ready",
        }:
            need(value is False, f"{key} must remain false")

    source_paths = {
        "electrical/panel/hr-v0-control-panel-p0.6/backplate-layout.csv": PANEL / "backplate-layout.csv",
        "electrical/panel/hr-v0-control-panel-p0.6/thermal-space-screen.csv": PANEL / "thermal-space-screen.csv",
        "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/panel-placement-screen.csv": R161 / "panel-placement-screen.csv",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/connector-schedule.csv": R202 / "connector-schedule.csv",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/pcb-placement.csv": R202 / "pcb-placement.csv",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/hr-v0-runtime-observation-carrier-p0.2.kicad_pcb": R202 / "hr-v0-runtime-observation-carrier-p0.2.kicad_pcb",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/connector-schedule.csv": R204 / "connector-schedule.csv",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/pcb-placement.csv": R204 / "pcb-placement.csv",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/harness-interface.csv": R204 / "harness-interface.csv",
    }
    need(set(status.get("source_hashes", {})) == set(source_paths), "source hash membership changed")
    for key, path in source_paths.items():
        need(path.is_file(), f"source missing: {key}")
        if path.is_file():
            need(status["source_hashes"].get(key) == digest(path), f"source hash mismatch: {key}")

    placements = {r["reference"]: r for r in rows(ENG / "panel-placement.csv")}
    obs_row = placements.get("OBS1 / R202 carrier", {})
    need((obs_row.get("x_mm"), obs_row.get("y_mm"), obs_row.get("width_mm"), obs_row.get("height_mm")) == ("433.0", "300.0", "90.0", "120.0"), "OBS1 placement changed")
    need(obs_row.get("rotation") == "90 deg counterclockwise", "OBS1 rotation changed")
    need(placements.get("PIOBS1 / R204 carrier", {}).get("state") == "REFERENCE TRANSFORM ONLY - RECEIVED OFFSET UNKNOWN", "Pi carrier reference state changed")

    obs = (433.0, 300.0, 90.0, 120.0)
    panel = (0.0, 0.0, 533.4, 685.8)
    need(obs[0] >= panel[0] and obs[1] >= panel[1] and obs[0] + obs[2] <= panel[2] and obs[1] + obs[3] <= panel[3], "OBS1 outside nominal backplate")
    blockers = {
        "WD2": (383.8, 10.0, 40.0, 665.8), "GTM3": (440.0, 250.0, 63.5, 25.4),
        "protection reserve": (250.0, 375.0, 127.8, 140.0),
        "LIM1": (54.0, 538.0, 100.0, 60.0), "LIM2": (164.0, 538.0, 100.0, 60.0), "LIM3": (54.0, 608.0, 100.0, 60.0),
    }
    for name, rect in blockers.items():
        need(not overlap(obs, rect), f"OBS1 overlaps {name}")

    source_place = {r["reference"]: r for r in rows(R202 / "pcb-placement.csv")}
    def transform(ref: str) -> tuple[float, float]:
        row = source_place[ref]; x, y = float(row["x_mm"]), float(row["y_mm"])
        return 433.0 + y, 300.0 + 120.0 - x
    need(transform("JLOGIC1") == (478.0, 306.0), "JLOGIC1 transform wrong")
    need(transform("JFIELD1") == (478.0, 414.0), "JFIELD1 transform wrong")
    expected_holes = {"MH1": (437.5, 415.5), "MH2": (437.5, 304.5), "MH3": (518.5, 415.5), "MH4": (518.5, 304.5)}
    holes = rows(ENG / "mounting-hole-screen.csv")
    need(len(holes) == 4, "four transformed holes required")
    for row in holes:
        point = (float(row["candidate_panel_x_mm"]), float(row["candidate_panel_y_mm"]))
        need(point == expected_holes.get(row["hole"]), f"hole transform changed: {row['hole']}")
        need(row["panel_hole"] == "SELECTION REQUIRED - DO NOT DRILL", f"hole released: {row['hole']}")

    route_rows = rows(ENG / "harness-route.csv")
    grouped: dict[str, list[tuple[int, tuple[float, float]]]] = {}
    for row in route_rows:
        grouped.setdefault(row["route_id"], []).append((int(row["node"]), (float(row["x_mm"]), float(row["y_mm"]))))
        need(row["state"] == "ROUTE SCREEN ONLY - DO NOT CUT OR INSTALL", f"route state changed: {row['route_id']}")
    compute = [point for _, point in sorted(grouped.get("PIOI-ROUTE-COMPUTE", []))]
    field = [point for _, point in sorted(grouped.get("PIOI-ROUTE-FIELD", []))]
    need(len(compute) == 4 and abs(manhattan(compute) - 335.4) < 0.01, "compute route does not reproduce 335.4 mm")
    need(len(field) == 4 and abs(manhattan(field) - 276.0) < 0.01, "field route does not reproduce 276.0 mm")
    need(compute[1][0] == compute[2][0] == 403.8 and field[1][0] == field[2][0] == 403.8, "route not on WD2 centreline")
    need(compute[2][1] == 306.0 and field[2][1] == 342.0 and field[2][1] - compute[2][1] == 36.0, "nominal compute/field route gap changed")

    lengths = {r["route_id"]: r for r in rows(ENG / "harness-length-calculation.csv")}
    need(lengths.get("PIOI-ROUTE-COMPUTE", {}).get("nominal_centerline_mm") == "335.4", "compute length row changed")
    need(lengths.get("PIOI-ROUTE-FIELD", {}).get("nominal_centerline_mm") == "276.0", "field length row changed")
    need(all(r["cut_length_mm"] == "SELECTION REQUIRED" and r["state"] == "GEOMETRIC SCREEN ONLY" for r in lengths.values()), "a route was falsely released")

    parity = rows(ENG / "interface-parity.csv")
    expected = {
        ("FIELD", "1"): ("SR1_STATUS", "XT1-03", "JFIELD1.1"), ("FIELD", "2"): ("SRA1_STATUS", "XT1-04", "JFIELD1.2"),
        ("FIELD", "3"): ("K1_STATUS", "XT1-05", "JFIELD1.3"), ("FIELD", "4"): ("K2_STATUS", "XT1-06", "JFIELD1.4"),
        ("FIELD", "5"): ("SAFETY_0V", "XT1-02", "JFIELD1.5"),
        ("COMPUTE", "1"): ("PI_3V3_CANDIDATE", "JLOGIC1.1", "JOBS1.1"), ("COMPUTE", "2"): ("COMPUTE_0V", "JLOGIC1.2", "JOBS1.2"),
        ("COMPUTE", "3"): ("OBS_SR1_PI", "JLOGIC1.3", "JOBS1.3"), ("COMPUTE", "4"): ("OBS_SRA1_PI", "JLOGIC1.4", "JOBS1.4"),
        ("COMPUTE", "5"): ("OBS_K1_PI", "JLOGIC1.5", "JOBS1.5"), ("COMPUTE", "6"): ("OBS_K2_PI", "JLOGIC1.6", "JOBS1.6"),
    }
    need(len(parity) == 11 and {(r["domain"], r["conductor"]) for r in parity} == set(expected), "interface parity membership changed")
    for row in parity:
        need((row["net"], row["from"], row["to"]) == expected[(row["domain"], row["conductor"])], f"interface mapping changed: {row['domain']} {row['conductor']}")
        need(row["parity_result"] == "SOURCE-PARITY PASS" and row["physical_state"] == "NOT BUILT / NOT CONNECTED", "interface physical state changed")

    r202_conn = {(r["reference"], r["terminal"]): r["net"] for r in rows(R202 / "connector-schedule.csv")}
    r204_conn = {(r["reference"], r["terminal"]): r["net"] for r in rows(R204 / "connector-schedule.csv")}
    r204_harness = {r["conductor"]: (r["net"], r["from"], r["to"]) for r in rows(R204 / "harness-interface.csv")}
    for pin in map(str, range(1, 7)):
        net = expected[("COMPUTE", pin)][0]
        need(r202_conn.get(("JLOGIC1", pin)) == net, f"R202 JLOGIC1 source mismatch: {pin}")
        need(r204_conn.get(("JOBS1", pin)) == net, f"R204 JOBS1 source mismatch: {pin}")
        need(r204_harness.get(pin) == expected[("COMPUTE", pin)], f"R204 harness source mismatch: {pin}")
    for pin in map(str, range(1, 6)):
        need(r202_conn.get(("JFIELD1", pin)) == expected[("FIELD", pin)][0], f"R202 JFIELD1 source mismatch: {pin}")

    holds = rows(ENG / "selection-holds.csv")
    acceptance = rows(ENG / "acceptance-matrix.csv")
    need(len(holds) == 13 and all(r["state"] == "OPEN - SELECTION/EVIDENCE REQUIRED" and not r["evidence_uri"] for r in holds), "thirteen holds must remain open")
    need(len(acceptance) == 16 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in acceptance), "sixteen acceptance rows must remain open")

    for name in common - {"SOURCE-MANIFEST.csv"}:
        need((ENG / name).read_bytes() == (WEB / name).read_bytes(), f"engineering/web mismatch: {name}")
    page = (WEB / "index.html").read_text(encoding="utf-8")
    for token in ("font:16px", "font-size:14px", "min-width:820px", "The boards fit on paper. The wires still need measuring.", "335.4 mm", "276.0 mm", "SELECTION REQUIRED", WARNING):
        need(token in page, f"web guide token missing: {token}")
    svg = (WEB / "panel-integration.svg").read_text(encoding="utf-8")
    for token in ("font:700 16px", "font:14px", "font:13px", "CCASE1 / Pi stack area", "R204 ref.", "R202 receiver", "R161 DXL", WARNING):
        need(token in svg, f"diagram token missing: {token}")

    for directory in (ENG, WEB):
        manifest = rows(directory / "SOURCE-MANIFEST.csv")
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "SOURCE-MANIFEST.csv"}
        need({r["file"] for r in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["file"]
            need(row["sha256"] == digest(path).upper(), f"manifest digest mismatch: {directory.name}/{row['file']}")

    required_docs = [
        ROOT / "docs/hr-v0-pi-observation-integration-p0.1.md",
        ROOT / "docs/reviews/2026-08-10-r205-independent-review-request.md",
        ROOT / "docs/reviews/2026-08-10-r205-validation-record.md",
        ROOT / "docs/reviews/2026-08-10-sol-r12-post-r205-status.md",
    ]
    for path in required_docs:
        need(path.is_file() and WARNING in path.read_text(encoding="utf-8"), f"required controlled doc missing/warning absent: {path.name}")

    if failures:
        print("HR-V0-PI-OBS-INTEGRATION-P0.1 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-PI-OBS-INTEGRATION-P0.1 PASS")
    print("  R202 rotated placement avoids WD2, GTM3, protection reserve and R161 lower carriers")
    print("  335.4 mm compute and 276.0 mm field screens; all cut lengths remain SELECTION REQUIRED")
    print("  13 holds / 16 acceptance rows OPEN; zero work or safety authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
