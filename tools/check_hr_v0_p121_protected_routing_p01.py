#!/usr/bin/env python3
"""Validate R240 P1.21 protected-routing candidate."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/p121-protected-routing-p0.1"
ENG = ROOT / "electrical/routing/hr-v0-p121-protected-routing-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def need(value, message):
    if not value:
        raise SystemExit(message)


def point(value):
    x, y = value.split(",")
    return float(x), float(y)


def segments(path_text):
    pts = [point(item.strip()) for item in path_text.split("|")]
    return list(zip(pts, pts[1:])), pts


def intersects(a, b):
    (x1,y1),(x2,y2)=a; (x3,y3),(x4,y4)=b
    if x1 == x2 and y3 == y4:
        return min(x3,x4) <= x1 <= max(x3,x4) and min(y1,y2) <= y3 <= max(y1,y2)
    if y1 == y2 and x3 == x4:
        return min(x1,x2) <= x3 <= max(x1,x2) and min(y3,y4) <= y1 <= max(y3,y4)
    if x1 == x2 == x3 == x4:
        return max(min(y1,y2),min(y3,y4)) <= min(max(y1,y2),max(y3,y4))
    if y1 == y2 == y3 == y4:
        return max(min(x1,x2),min(x3,x4)) <= min(max(x1,x2),max(x3,x4))
    return False


def main():
    for directory in (OUT, ENG):
        delta = rows(directory/"p121-route-delta.csv")
        need(len(delta) == 7, "route delta count")
        by_id = {r["record"]: r for r in delta}
        need(by_id["P2P-005"]["p121_from"] == "KWD2:14" and by_id["P2P-005"]["p121_to"] == "SRA1:A1" and by_id["P2P-005"]["p121_net"] == "SRA1_A1_WD_GATED", "P2P-005 stale")
        need(by_id["P2P-015"]["p121_net"] == "WD_SRA1_SUPPLY_INTERMEDIATE", "P2P-015 stale")
        need(by_id["P2P-035"]["p121_from"] == "XD24:02" and by_id["P2P-035"]["p121_to"] == "SR1:A1" and "SELECTION REQUIRED" in by_id["P2P-035"]["disposition"], "P2P-035 disposition")
        classes = rows(directory/"route-class-register.csv")
        need(len(classes) == 3 and next(r for r in classes if r["class_id"] == "DF01-GATE-HOT")["safety_credit"] == "ZERO SAFETY CREDIT", "route classes")
        need(len(rows(directory/"corridor-register.csv")) == 5, "corridor count")
        routes = rows(directory/"route-segment-register.csv")
        need(len(routes) == 9, "route count")
        parsed = {}
        for route in routes:
            segs, pts = segments(route["path_centerline_mm"])
            parsed[route["route_id"]] = segs
            need(all(0 <= x <= 533.4 and 0 <= y <= 685.8 for x,y in pts), f"route outside panel {route['route_id']}")
            calc = sum(abs(x2-x1)+abs(y2-y1) for (x1,y1),(x2,y2) in segs)
            need(abs(calc-float(route["planning_manhattan_mm"])) < 0.011, f"length {route['route_id']}")
            need(route["cut_length_mm"] == "SELECTION REQUIRED" and route["terminal_entry_coordinates"] == "SELECTION REQUIRED", f"physical value invented {route['route_id']}")
        hot = [r for r in routes if r["class_id"] in {"SF01-SUPPLY","DF01-GATE-HOT"}]
        credited = [r for r in routes if r["class_id"] == "SF01-INPUT"]
        expected_pairs = len(hot)*len(credited)
        screens = rows(directory/"crossing-screen.csv")
        need(len(screens) == expected_pairs, "crossing screen coverage")
        for h in hot:
            for c in credited:
                count = sum(1 for hs in parsed[h["route_id"]] for cs in parsed[c["route_id"]] if intersects(hs, cs))
                need(count == 0, f"route crossing {h['route_id']} {c['route_id']}")
        need(all(r["nominal_centerline_crossings"] == "0" for r in screens), "crossing claim")
        need(len(rows(directory/"prohibited-adjacency.csv")) == 6 and all(r["state"] == "OPEN" for r in rows(directory/"prohibited-adjacency.csv")), "adjacency controls")
        need(len(rows(directory/"inspection-register.csv")) == 8 and all(r["result"] == "NOT EXECUTED" and r["evidence"] == "BLANK" for r in rows(directory/"inspection-register.csv")), "inspection evidence")
        need(len(rows(directory/"open-holds.csv")) == 9 and all(r["state"] == "OPEN" for r in rows(directory/"open-holds.csv")), "open holds")
        need(len(rows(directory/"source-register.csv")) == 6, "source register")
        for name in ("p121-route-delta.csv","route-class-register.csv","corridor-register.csv","route-segment-register.csv","prohibited-adjacency.csv","crossing-screen.csv","inspection-register.csv","open-holds.csv","source-register.csv"):
            need(all(r["warning"] == WARNING for r in rows(directory/name)), f"warning {name}")
        status = json.loads((directory/"package-status.json").read_text(encoding="utf-8"))
        need(status["nominal_centerline_crossings"] == 0 and status["open_holds"] == 9, "status counts")
        need(status["current_candidate"] == "V3-P1.15-CARRIER-CANDIDATE" and not status["p121_accepted"], "configuration promoted")
        need(not status["protected_route_released"] and not status["physical_evidence_complete"] and not status["qualified_review_complete"] and not status["functional_safety_approved"] and not status["work_authority"], "authority promoted")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"Keep watchdog hot conductors away from credited inputs","SELECTION REQUIRED","0 nominal crossings","same R12 independent review","font-size:14px"):
        need(token in page, f"guide {token}")
    need("font-size:12px" not in page and "font-size:11px" not in page, "undersized html text")
    svg=(OUT/"routing-overlay.svg").read_text(encoding="utf-8")
    need("viewBox=\"0 0 533.4 685.8\"" in svg and "font-size:12px" in svg and "font-size:11px" not in svg, "svg geometry/text")
    manifest={r["file"]:r for r in rows(OUT/"file-manifest.csv")}
    actual={p.name:p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest)==set(actual), "manifest membership")
    for name,path in actual.items():
        payload=path.read_bytes()
        need(manifest[name]["size_bytes"]==str(len(payload)) and manifest[name]["sha256"]==hashlib.sha256(payload).hexdigest().upper(), f"manifest {name}")
    print("PASS: R240 P1.21 protected-routing planning candidate; physical route and authority remain open")
    print(WARNING)


if __name__ == "__main__":
    main()
