#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 head HMI physical harness candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "head-hmi-harness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_head_hmi_harness_p01.py"
WARNING = "PRELIMINARY - UNBUILT HEAD HMI HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    sources, bindings = rows(OUT / "primary-source-register.csv"), rows(OUT / "source-binding.csv")
    equipment, links = rows(OUT / "head-equipment-register.csv"), rows(OUT / "head-interface-link-register.csv")
    routes, controls = rows(OUT / "head-route-retention-register.csv"), rows(OUT / "privacy-control-boundary.csv")
    tests, holds = rows(OUT / "inspection-test-plan.csv"), rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "head-hmi-status.json").read_text(encoding="utf-8"))
    need(len(sources) == 11 and len(bindings) == 6, "source coverage drift")
    need(len(equipment) == 8 and len(links) == len(routes) == 11, "equipment/link/route coverage drift")
    need(len(controls) == 8 and len(tests) == 12 and len(holds) == 10, "control/test/hold coverage drift")
    all_rows = sources + bindings + equipment + links + routes + controls + tests + holds
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for r in all_rows), "execution/warning overclaim")
    need(all(r["physical_link_built"] == "NO" for r in links), "physical link falsely built")
    need(all(r["neck_worst_pose_checked"] == r["interference_checked"] == "NO" for r in routes), "route validation overclaim")
    need(all(r["validated"] == "NO" for r in controls), "privacy/control validation overclaim")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in tests), "test execution overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["sha256"] == sha(ROOT / r["path"]) and int(r["bytes"]) == (ROOT / r["path"]).stat().st_size for r in bindings), "source binding drift")

    cameras = [r for r in links if "vision" in r["service"]]
    need(len(cameras) == 2 and all("22-way" in r["from_interface"] and "15-pin" in r["to_interface"] for r in cameras), "camera connector correction drift")
    need(all(r["candidate_length_mm"] == "300" and int(r["length_margin_mm"]) >= 79 for r in cameras), "camera length candidate regressed")
    need(all("OPAQUE MANUFACTURER CABLE" in r["contact_definition"] for r in cameras), "camera cable internal pinout invented")
    need(not any("22-pin CSI FFC via 200 mm" in r["connector_boundary"] for r in equipment), "obsolete camera boundary survived")
    need(any("100099135" in r["candidate"] for r in equipment) and any("114993346" in r["candidate"] for r in equipment), "audio candidates missing")
    need(any("MF30100V3-10000-A99" in r["candidate"] for r in equipment), "fan candidate missing")
    need(any("direct GPIO stacking rejected" in r["connector_boundary"] for r in equipment if r["item_id"] == "EQ-H01-DISPLAY"), "display remote-interface rule missing")
    for key in ["physical_fit_verified", "privacy_controls_validated", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["received_hardware_count"] == status["built_link_count"] == status["executed_test_count"] == 0, "physical evidence overclaim")
    need(status["camera_interface_corrected"] and status["former_200_mm_camera_assumption_rejected"], "correction disposition missing")

    need((OUT / "head-hmi-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    page, svg = (OUT / "index.html").read_text(encoding="utf-8"), (OUT / "head-hmi-harness.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1200px" in page, "web legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:32px" in svg, "drawing legibility drift")
    need("The robot now has a routed head nervous system" in page, "guide purpose drift")
    need("HR30-HEAD-HMI-HARNESS-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["head_hmi_equipment_count"] == 8 and root_status["head_hmi_physical_link_count"] == 11, "root status integration missing")
    need(root_status["head_hmi_camera_interface_corrected"] and not root_status["energization_authority"], "root correction/authority boundary drift")
    print("PASS: HR-30 head HMI harness has 8 equipment records, 11 physical links, two corrected 22-to-15 camera links, 0 built links, and no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
