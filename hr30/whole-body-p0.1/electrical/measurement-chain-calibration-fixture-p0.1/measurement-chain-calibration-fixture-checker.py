#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 off-robot calibration fixture P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

try:
    import pcbnew
except ModuleNotFoundError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "measurement-chain-calibration-fixture-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
PODS = WHOLE / "electrical" / "diagnostic-pickoff-pods-p0.1"
PANEL = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
HARNESS = WHOLE / "first-energization-measurement-harness-p0.1"
INSTR = WHOLE / "first-energization-instrumentation-p0.1"
PROJECT = "hr30-measurement-chain-calibration-fixture-p0.1"
WARNING = "PRELIMINARY - UNBUILT OFF-ROBOT MEASUREMENT CALIBRATION FIXTURE - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION TO THE ROBOT, POWERED ROBOT TESTING, MOTION, WALKING OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_board() -> None:
    board = pcbnew.LoadBoard(str(OUT / "board" / f"{PROJECT}.kicad_pcb"))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(set(refs) == {"JPS","JHI","JLO","JDUT","H1","H2","H3","H4"}, "board reference set drift")
    board.BuildConnectivity()
    need(board.GetConnectivity().GetUnconnectedCount(False) == 0, "unconnected board pads")
    need(sum(isinstance(item, pcbnew.PCB_TRACK) for item in board.GetTracks()) >= 8, "board routing missing")
    points = []
    for item in board.GetDrawings():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            points += [item.GetStart(), item.GetEnd()]
    xs = [pcbnew.ToMM(p.x) for p in points]; ys = [pcbnew.ToMM(p.y) for p in points]
    need(abs(max(xs)-min(xs)-104.0) < 1e-6 and abs(max(ys)-min(ys)-76.0) < 1e-6, "board envelope drift")
    nets = {net.GetNetname() for net in board.GetNetInfo().NetsByName().values() if net.GetNetname()}
    need(nets == {"CAL_HI","CAL_LO"}, "unexpected net or shared reference")


def main() -> int:
    if pcbnew is None:
        exe = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
        return subprocess.run([str(exe), str(Path(__file__).resolve())], check=False).returncode
    ports = rows("fixture-port-register.csv")
    channels = rows("calibration-channel-register.csv")
    points = rows("calibration-point-register.csv")
    procedures = rows("procedure-register.csv")
    faults = rows("fault-injection-register.csv")
    schema = rows("data-schema-register.csv")
    holds = rows("open-holds.csv")
    sources = rows("primary-source-register.csv")
    need(len(ports) == 6 and {r["connector"] for r in ports} == {"JPS","JHI","JLO","JDUT"}, "two two-contact Phoenix ports plus two one-contact DMM safety jacks required")
    need({r["net"] for r in ports} == {"CAL_HI","CAL_LO"} and all(r["robot_connection_permitted"] == "NO" for r in ports), "floating port boundary drift")
    need(len(channels) == 8 and {r["channel_id"] for r in channels} == {f"CH-AI-{i:02d}" for i in range(1,9)}, "eight channel set drift")
    need(all(r["simultaneous_fixture_channels"] == "1" and r["robot_disconnected_required"] == "YES" for r in channels), "sequential off-robot invariant failed")
    need(len(points) == 72, "72 scheduled calibration points required")
    need(all(r["repeat_count"] == "3" and r["source_current_limit_candidate_ma"] == "10" and r["state"] == "NOT EXECUTED" for r in points), "point schedule/repeat/execution drift")
    need(all(sum(1 for row in points if row["channel_id"] == cid) == 9 for cid in {r["channel_id"] for r in channels}), "nine points per channel required")
    need(len(procedures) == 15 and len(faults) == 8 and len(schema) >= 18, "procedure/fault/data completeness drift")
    need(all(r["execution_state"] == "NOT EXECUTED" for r in procedures + faults), "unexecuted evidence improperly claimed")
    need(len(holds) == 9 and all(r["state"] == "OPEN" for r in holds), "open holds drift")
    need(len(sources) == 8 and all(r["url"].startswith("https://") for r in sources), "primary-source register incomplete")
    need({r["header"] for r in ports if r["connector"] in {"JHI","JLO"}} == {"Pomona 73099-2 red","Pomona 73099-0 black"}, "DMM safety-jack candidates drift")
    need(all(r["mating_plug"] == "Fluke TL930 4 mm patch cord" for r in ports if r["connector"] in {"JHI","JLO"}), "DMM patch-lead boundary drift")
    status = json.loads((OUT / "calibration-fixture-status.json").read_text(encoding="utf-8"))
    need(status["channel_count"] == 8 and status["simultaneous_fixture_channels"] == 1 and status["scheduled_points"] == 72, "status count drift")
    for key in ["robot_connection_permitted","fixture_built","fixture_inspection_executed","instrument_calibration_verified","calibration_executed","uncertainty_accepted","numeric_acceptance_limits_released","fer_g11_closed","functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_robot_test_authority","motion_authority","walking_authority","energization_authority"]:
        need(status[key] is False, f"unsafe or unsupported status true: {key}")
    need("0  Errors 0  Warnings 0" in (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8"), "ERC not 0/0")
    drc = (OUT / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "DRC not zero")
    binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    for path, key in [
        (PODS / "source-node-register.csv", "diagnostic_pod_channels_sha256"),
        (PODS / "end-to-end-scale-register.csv", "diagnostic_pod_scale_sha256"),
        (PANEL / "channel-register.csv", "measurement_panel_channels_sha256"),
        (HARNESS / "channel-endpoint-register.csv", "measurement_harness_endpoints_sha256"),
        (INSTR / "instrument-register.csv", "instrument_register_sha256"),
    ]:
        need(binding[key] == digest(path), f"source binding drift: {key}")
    check_board()
    manifest = rows("file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest file set drift")
    for row in manifest:
        path = OUT / row["path"]
        need(int(row["bytes"]) == path.stat().st_size and row["sha256"] == digest(path), f"manifest mismatch: {path}")
        need(row["warning"] == WARNING, f"warning drift: {path}")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    need(source_files == release_files, "source/release file set drift")
    for rel in source_files:
        need((OUT/rel).read_bytes() == (REL/rel).read_bytes(), f"source/release byte drift: {rel}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "measurement-chain-calibration-fixture-p0.1/index.html" in root_page, "interactive guide/legibility integration missing")
    need((OUT / "HR30_measurement_chain_calibration_fixture_candidate.step").stat().st_size > 100000, "STEP appears incomplete")
    need((OUT / "HR30_measurement_chain_calibration_fixture_candidate.glb").stat().st_size > 10000, "GLB appears incomplete")
    print("PASS: one-channel off-robot calibration fixture, 8 lanes, 72 points x3, native KiCad ERC 0/0 and DRC 0; build/execution/FER-G11/all robot authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
