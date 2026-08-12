#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-A04-JOINT-P0.1."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "mechanical/joints/hr-v0-a04-joint-p0.1"
REL = ROOT / "release/hr-v0/a04-joint-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)

def check_manifest(directory: Path) -> None:
    records = rows(directory / "file-manifest.csv")
    files = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    require(len(records) == len(files), f"manifest count mismatch: {directory}")
    by_name = {r["relative_path"]: r for r in records}
    for p in files:
        rel = p.relative_to(directory).as_posix()
        require(rel in by_name, f"manifest missing {rel}")
        require(by_name[rel]["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest(), f"hash mismatch {rel}")
        require(by_name[rel]["warning"] == WARNING, f"warning mismatch {rel}")

def main() -> int:
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == "HR-V0-A04-JOINT-P0.1" and status["round"] == "R274", "identity mismatch")
    for flag in ("hardware_selected","procurement_authorized","assembly_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        require(status[flag] is False, f"authority flag must remain false: {flag}")
    sources = rows(PKG / "source-register.csv")
    schedule = rows(PKG / "exact-candidate-schedule.csv")
    screens = rows(PKG / "analytical-screen.csv")
    require(len(sources) == 8 and len(schedule) == 5 and len(screens) == 6, "record count mismatch")
    require([r["supplier_order_code"] for r in schedule] == ["91290A303","98688A148","90576A161","36852","26060"], "exact candidate mismatch")
    require(all("CANDIDATE HOLD" in r["selection_state"] for r in schedule), "candidate promoted")
    require(len(rows(PKG / "received-stack-measurements.csv")) == 10, "receiving count mismatch")
    require(len(rows(PKG / "torque-preload-development.csv")) == 12, "torque trial count mismatch")
    require(len(rows(PKG / "installation-traveler.csv")) == 4, "installation axis count mismatch")
    require(len(rows(PKG / "verification-plan.csv")) == 7, "verification plan count mismatch")
    holds = rows(PKG / "open-holds.csv")
    acc = rows(PKG / "acceptance-matrix.csv")
    require(len(holds) == 12 and len(acc) == 12, "hold/acceptance count mismatch")
    require(all(r["state"] == "OPEN" and r["execution"] == "NOT EXECUTED" for r in holds), "hold improperly closed")
    require(all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" for r in acc), "acceptance improperly closed")
    as_mm2 = math.pi/4*(2.5-0.9382*0.45)**2
    vm = math.sqrt((392.085/as_mm2)**2 + 3*(112.275/as_mm2)**2)
    require(abs(vm - 129.073) < 0.01, "combined stress arithmetic changed")
    html_text = (PKG / "index.html").read_text(encoding="utf-8")
    require("font:clamp(16px" in html_text and "font-size:14px" in html_text, "legibility floor missing")
    require(WARNING in html_text and "zero selection" in html_text, "web warning/boundary missing")
    require(PKG.joinpath("README.md").read_bytes() == REL.joinpath("README.md").read_bytes(), "release copy mismatch")
    check_manifest(PKG)
    check_manifest(REL)
    cfg = json.loads((ROOT / "configuration/hr-v0-config-reconciliation-p0.38/package-status.json").read_text(encoding="utf-8"))
    require(cfg["identifier"] == "HR-V0-CONFIG-REC-P0.38" and cfg["energization_authorized"] is False, "configuration mismatch")
    print("HR-V0 A04 joint P0.1 checks passed: 8 sources, 5 candidates, 12 holds, zero authority")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
