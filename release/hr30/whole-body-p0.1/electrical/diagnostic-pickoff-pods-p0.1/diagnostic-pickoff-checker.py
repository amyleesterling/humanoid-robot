#!/usr/bin/env python3
"""Fail-closed checker for HR-30 diagnostic pickoff pods P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import pcbnew
except ModuleNotFoundError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "diagnostic-pickoff-pods-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
PROJECT = "hr30-diagnostic-pickoff-pod-p0.1"
WARNING = "PRELIMINARY - UNBUILT SOURCE-LOCAL DIAGNOSTIC PICKOFF PODS - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value: raise RuntimeError(message)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_board() -> None:
    board = pcbnew.LoadBoard(str(OUT / "board" / f"{PROJECT}.kicad_pcb"))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(set(refs) == {"JIN","JOUT","RHA","RHB","RLA","RLB","H1","H2","H3","H4"}, "board reference set drift")
    need(sum(isinstance(item, pcbnew.PCB_TRACK) for item in board.GetTracks()) >= 6, "board routing missing")
    board.BuildConnectivity()
    need(board.GetConnectivity().GetUnconnectedCount(False) == 0, "unconnected board pads")
    edge_points = []
    for item in board.GetDrawings():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            edge_points += [item.GetStart(), item.GetEnd()]
    xs = [pcbnew.ToMM(p.x) for p in edge_points]; ys = [pcbnew.ToMM(p.y) for p in edge_points]
    need(abs(max(xs)-min(xs)-74.0) < 1e-6 and abs(max(ys)-min(ys)-34.0) < 1e-6, "board envelope drift")


def main() -> int:
    if pcbnew is None:
        exe = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
        return subprocess.run([str(exe), str(Path(__file__).resolve())], check=False).returncode
    nodes = rows("source-node-register.csv"); pods = rows("pod-assembly-register.csv"); contacts = rows("connector-contact-map.csv"); resistors = rows("resistor-register.csv"); cables = rows("source-to-panel-cable-register.csv"); scale = rows("end-to-end-scale-register.csv"); faults = rows("fault-boundary-register.csv"); holds = rows("open-holds.csv"); sources = rows("primary-source-register.csv")
    need(len(nodes) == len(pods) == len(scale) == 8, "eight-channel/pod register mismatch")
    need({r["channel_id"] for r in nodes} == {f"CH-AI-{i:02d}" for i in range(1,9)}, "channel set drift")
    need(len({r["pod_id"] for r in nodes}) == 8 and all(r["source_tail_max_mm"] == "100" for r in nodes), "one-pod-per-source boundary drift")
    need(len(contacts) == 32 and len(cables) == 16 and len(resistors) == 32, "contact/cable/resistor count drift")
    need(all(sum(1 for x in resistors if x["pod_id"] == pod and x["lead"] == lead) == 2 for pod in {r["pod_id"] for r in nodes} for lead in ("HI","LO")), "two-resistors-per-lead invariant failed")
    need(all(r["order_code"] == "TNPW1206100KBEEA" and r["operating_voltage_rating_v"] == "200" for r in resistors), "resistor candidate drift")
    need(all(abs(float(r["nominal_scale_correction"])-1.4204) < 1e-6 for r in scale), "composite scale drift")
    need(any(r["fault_id"] == "DP-F06" and r["disposition"].startswith("BLOCKER") for r in faults), "upstream source-tail blocker missing")
    need(len(holds) == 8 and all(r["state"] == "OPEN" for r in holds), "open holds drift")
    need(len(sources) >= 6 and all(r["url"].startswith("https://") for r in sources), "primary sources incomplete")
    status = json.loads((OUT / "pod-status.json").read_text(encoding="utf-8"))
    need(status["pod_count"] == 8 and status["one_pod_per_channel"] is True and status["long_cable_upstream_of_resistors"] is False, "pod topology status drift")
    need(status["source_terminal_taps_selected"] is False and status["source_tails_validated"] is False, "source boundary improperly closed")
    for key in ["functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority","fer_g11_closed"]:
        need(status[key] is False, f"unsafe authority/status true: {key}")
    need("0  Errors 0  Warnings 0" in (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8"), "ERC not 0/0")
    drc = (OUT / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "DRC not zero")
    binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    for path, key in [
        (WHOLE / "first-energization-measurement-harness-p0.1/channel-endpoint-register.csv", "measurement_harness_channels_sha256"),
        (WHOLE / "electrical/measurement-boundary-panel-p0.1/channel-register.csv", "measurement_panel_channels_sha256"),
        (WHOLE / "electrical/tether-power-core-p0.1/net-schedule.csv", "tether_power_net_schedule_sha256"),
        (WHOLE / "electrical/kicad/hr30-whole-body-electrical-p0.1/net-schedule.csv", "whole_body_net_schedule_sha256"),
    ]: need(binding[key] == digest(path), f"source binding drift: {key}")
    check_board()
    manifest = rows("file-manifest.csv"); expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest file set drift")
    for row in manifest:
        path = OUT / row["path"]; need(int(row["bytes"]) == path.stat().st_size and row["sha256"] == digest(path), f"manifest mismatch: {path}"); need(row["warning"] == WARNING, f"warning drift: {path}")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()); release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    need(source_files == release_files, "source/release file set drift")
    for rel in source_files: need((OUT/rel).read_bytes() == (REL/rel).read_bytes(), f"source/release byte drift: {rel}")
    page = (OUT / "index.html").read_text(encoding="utf-8"); root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "diagnostic-pickoff-pods-p0.1/index.html" in root_page, "interactive guide/legibility integration missing")
    print("PASS: 8 source-local pods, 32 resistor records, native KiCad ERC 0/0 and DRC 0; source taps/build/calibration/FER-G11/all authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
