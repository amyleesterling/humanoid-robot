#!/usr/bin/env python3
"""Validate the HR-30 staged protection/conductor package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "protection-conductor-architecture-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
WARNING = "PRELIMINARY - PROTECTION AND CONDUCTOR ARCHITECTURE ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    required = {
        "README.md", "index.html", "protection-hierarchy.svg", "source-binding.csv", "primary-source-register.csv",
        "power-state-separation-register.csv", "protection-layer-register.csv", "bus-envelope.csv", "bus-source-feed-envelope.csv",
        "axis-conductor-screen.csv", "connector-bottleneck-register.csv", "closure-input-register.csv", "open-holds.csv",
        "protection-conductor-status.json", "file-manifest.csv",
    }
    require(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    require({p.name for p in OUT.iterdir()} == required, "unexpected source package file set")
    require({p.name for p in RELEASE.iterdir()} == required, "unexpected release package file set")
    for name in required:
        require(sha(OUT / name) == sha(RELEASE / name), f"source/release mismatch: {name}")

    status = json.loads((OUT / "protection-conductor-status.json").read_text(encoding="utf-8"))
    require(status["power_state_count"] == 8 and status["bus_feed_count"] == 8 and status["axis_screen_count"] == 25, "package counts wrong")
    require(status["bus_count"] == 8 and status["closure_input_count"] == 14 and status["open_hold_count"] == 10, "register counts wrong")
    require(abs(status["candidate_cap_sum_a"] - 46.67779) < 1e-6, "candidate cap total wrong")
    require(abs(status["published_stall_endpoint_sum_a"] - 71.88) < 1e-6, "stall endpoint total wrong")
    require(abs(status["candidate_cap_sum_source_shortfall_a"] - 4.97779) < 1e-6, "source shortfall wrong")
    require(status["candidate_cap_sum_a"] > status["candidate_source_continuous_a"], "source mismatch not exposed")
    for key in ("main_fuse_selected", "eight_feed_fuses_selected", "hot_conductor_ampacity_released", "regenerative_energy_architecture_released", "procurement_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        require(status[key] is False, f"authority/selection must remain false: {key}")

    bindings = rows("source-binding.csv")
    require(len(bindings) == 9, "source binding count wrong")
    for row in bindings:
        path = ROOT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"source binding mismatch: {row['binding_id']}")

    states = rows("power-state-separation-register.csv")
    require(len(states) == 8 and {r["state_id"] for r in states} == {f"FER-E{i}" for i in range(8)}, "state ladder wrong")
    e2 = next(r for r in states if r["state_id"] == "FER-E2")
    require("physically absent" in e2["mandatory_physical_separation"] and e2["motion_permitted"] == "NO", "logic-only separation weakened")
    require(all(r["motion_permitted"] == "NO" for r in states), "motion permitted in readiness ladder")

    buses = rows("bus-envelope.csv")
    feeds = rows("bus-source-feed-envelope.csv")
    axes = rows("axis-conductor-screen.csv")
    require(len(buses) == 8 and len(feeds) == 8 and len(axes) == 25, "power boundary count wrong")
    require(abs(sum(float(r["candidate_cap_sum_a"]) for r in buses) - 46.67779) < 1e-6, "bus cap arithmetic wrong")
    require(abs(sum(float(r["published_stall_endpoint_sum_a"]) for r in buses) - 71.88) < 1e-6, "bus stall arithmetic wrong")
    require(abs(sum(float(r["candidate_cap_sum_a"]) for r in feeds) - 46.67779) < 1e-6, "feed cap arithmetic wrong")
    require(abs(sum(float(r["published_stall_endpoint_sum_a"]) for r in feeds) - 71.88) < 1e-6, "feed stall arithmetic wrong")
    require({r["branch_id"] for r in feeds} == {f"FB{i}" for i in range(1, 9)}, "eight feed identities wrong")
    require(len({r["feed_target"] for r in feeds}) == 8, "feed targets are not electrically separate")
    require(all(r["fuse_value_a"] == "SELECTION REQUIRED" and r["fuse_order_code"] == "SELECTION REQUIRED" for r in feeds), "fuse selection invented")
    require(all(r["hot_bundled_ampacity"] == "SELECTION REQUIRED" and r["branch_protection"] == "SELECTION REQUIRED" for r in axes), "axis selection invented")
    require(all(r["headline_margin_is_ampacity_credit"].startswith("NO") for r in axes), "JST headline misused")

    layers = rows("protection-layer-register.csv")
    holds = rows("open-holds.csv")
    require(len(layers) == 7 and any("no released sink" in r["candidate_mechanism"] for r in layers), "regeneration boundary missing")
    require(len(holds) == 10 and all(r["state"] == "OPEN" for r in holds), "holds not fail-closed")
    require(all(r["warning"] == WARNING for name in ("source-binding.csv", "primary-source-register.csv", "power-state-separation-register.csv", "protection-layer-register.csv", "bus-envelope.csv", "bus-source-feed-envelope.csv", "axis-conductor-screen.csv", "connector-bottleneck-register.csv", "closure-input-register.csv", "open-holds.csv") for r in rows(name)), "warning drift")

    manifest = rows("file-manifest.csv")
    require(len(manifest) == len(required) - 1, "manifest count wrong")
    for row in manifest:
        path = OUT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {row['path']}")
        require(row["warning"] == WARNING, f"manifest warning drift: {row['path']}")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    require("46.678 A" in page and "71.88 A" in page and "41.7 A" in page, "web constraint summary missing")
    require("Eight electrically separate whole-robot feeds" in page and "five protected feeds" not in page and "five PDU" not in page, "stale five-board web architecture")
    diagram = (OUT / "protection-hierarchy.svg").read_text(encoding="utf-8")
    require("FB1–FB8" in diagram and "Eight one-bus boards" in diagram and "Five PDU" not in diagram, "stale five-board diagram architecture")
    require("font-size:16px" in page and "font-size:14px" in page, "web legibility floor missing")
    require("font-size:11" not in page and "font-size:10" not in page, "undersized web text")
    require((WHOLE / "README.md").read_text(encoding="utf-8").count("HR30-PROTECTION-CONDUCTOR-P01-README-START") == 1, "README integration missing/duplicated")
    require((WHOLE / "index.html").read_text(encoding="utf-8").count("HR30-PROTECTION-CONDUCTOR-P01-START") == 1, "whole-body web integration missing/duplicated")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    require(root_status["protection_conductor_architecture_present"] is True and root_status["protection_conductor_energization_authority"] is False, "root status integration wrong")
    require(root_status["protection_conductor_feed_count"] == 8 and root_status["eight_feed_fuses_selected"] is False, "root eight-feed status wrong")
    print("PASS: HR-30 staged protection/conductor architecture; all physical selections and authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
