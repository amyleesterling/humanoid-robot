"""Fail-closed checks for HR-30 harness/current-policy reconciliation."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "current-policy-binding-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / "current-policy-binding-p0.1"
GEN = ROOT / "tools" / "generate_hr30_harness_current_policy_binding_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    axis = rows(OUT / "axis-power-policy-binding.csv")
    buses = rows(OUT / "bus-power-boundary.csv")
    decisions = rows(OUT / "architecture-decision-register.csv")
    holds = rows(OUT / "open-holds.csv")
    sources = rows(OUT / "source-binding.csv")
    status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
    need(len(axis) == 25 and len({r["axis_id"] for r in axis}) == 25, "25 unique axis bindings required")
    need(len({r["pair_id"] for r in axis}) == 25, "25 unique power-pair bindings required")
    need(len(buses) == 8 and sum(int(r["axis_count"]) for r in buses) == 25, "eight-bus/25-axis coverage required")
    need(len(decisions) == 5 and len(holds) == 7 and all(r["state"] == "OPEN" for r in holds), "decision/hold coverage drift")
    need(len(sources) == 6 and all(r["sha256"] == sha(ROOT / r["path"]) for r in sources[:4]), "source hash drift")
    stall = sum(float(r["published_stall_endpoint_a"]) for r in axis)
    cap = sum(float(r["candidate_internal_limit_a"]) for r in axis)
    need(abs(stall - 71.88) < 1e-9 and abs(cap - 46.67779) < 1e-6, "whole-body current boundaries drift")
    need(all(r["internal_limit_below_catalog_boundary"] == "YES" for r in axis), "per-axis connector numeric screen failed")
    need(all(r["wire_construction"] == "SELECTION REQUIRED" and r["branch_protection"] == "SELECTION REQUIRED" for r in axis), "physical selection invented")
    by_bus: dict[str, list[dict]] = defaultdict(list)
    for row in axis:
        by_bus[row["bus_id"]].append(row)
        need(float(row["round_trip_planning_length_mm"]) > 0, f"missing routed length {row['axis_id']}")
        need("NOT CALCULATED" in row["voltage_drop_and_temperature"], "unreleased calculation overclaimed")
    for bus in buses:
        attached = by_bus[bus["bus_id"]]
        need(int(bus["axis_count"]) == len(attached), f"bus axis count drift {bus['bus_id']}")
        need(abs(float(bus["candidate_internal_cap_sum_a"]) - sum(float(r["candidate_internal_limit_a"]) for r in attached)) < 1e-6, "bus cap arithmetic drift")
        need(abs(float(bus["published_stall_endpoint_sum_a"]) - sum(float(r["published_stall_endpoint_a"]) for r in attached)) < 1e-6, "bus stall arithmetic drift")
    need(status["axis_binding_count"] == 25 and status["bus_binding_count"] == 8, "status count drift")
    for key in ["stall_endpoint_used_as_normal_demand", "internal_cap_used_as_harness_rating", "normal_rms_demand_selected", "wire_construction_selected", "branch_protection_selected", "voltage_drop_calculated", "thermal_validated", "procurement_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need((OUT / "harness-current-policy-binding-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["harness_current_policy_bound_axis_count"] == 25, "root status binding missing")
    need(root_status["harness_stall_endpoint_used_as_normal_demand"] is False, "root status overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "71.88 A" in page and "46.678 A" in page, "interactive guide content/legibility drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("HR30-HARNESS-CURRENT-BINDING-P01-START" in root_page and "25 / 25" in root_page, "root guide integration missing")
    print("PASS: 25/25 HR-30 power pairs bound to current policy; 71.88 A stall and 46.67779 A internal-cap boundaries separated; conductors/protection/authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
