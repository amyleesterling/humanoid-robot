"""Fail-closed checks for HR-30 FIRST_POWER_NO_MOTION firmware evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SOURCE = ROOT / "firmware" / "hr30-motion-controller"
OUT = WHOLE / "firmware" / "hr30-motion-controller-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "firmware" / "hr30-motion-controller-p0.1"
GEN = ROOT / "tools/generate_hr30_motion_firmware_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "firmware source/release package missing")
    status = json.loads((OUT / "firmware-status.json").read_text(encoding="utf-8"))
    axes, buses = rows(OUT / "axis-binding.csv"), rows(OUT / "bus-binding.csv")
    actions, faults, holds = rows(OUT / "action-disposition.csv"), rows(OUT / "fault-response.csv"), rows(OUT / "open-holds.csv")
    ios, sources = rows(OUT / "io-binding.csv"), rows(OUT / "source-binding.csv")
    need(len(axes) == 25 and len({r["axis_id"] for r in axes}) == 25, "25 unique axes required")
    need([int(r["axis_index"]) for r in axes] == list(range(25)), "axis indices must be 0..24")
    need(len(buses) == 8 and len({r["bus_id"] for r in buses}) == 8, "eight unique buses required")
    need([int(r["bus_index"]) for r in buses] == list(range(8)), "bus indices must be 0..7")
    need(sum(int(r["axis_count"]) for r in buses) == 25, "bus axis sum must be 25")
    need(len(actions) == 10 and len(faults) == 6 and len(holds) == 10 and len(ios) == 10 and len(sources) == 11, "firmware register coverage drift")
    need(all(r["torque_command"] == "COMPILE-TIME DISABLED" and r["bus_transmit"] == "COMPILE-TIME DISABLED" for r in axes), "axis output path enabled")
    need(all(r["transmit_enable"] == "COMPILE-TIME DISABLED" for r in buses), "bus transmit path enabled")
    need(all(r["motion_possible"] == "NO" and r["torque_enable_mask"] == "0x00000000" and r["bus_tx_enable_mask"] == "0x0000" for r in actions), "action disposition permits motion")
    need(sum(r["first_power_profile_disposition"].startswith("ACCEPT") for r in actions) == 1, "only STOP may be accepted")
    need(next(r for r in actions if r["action"] == "STOP_REQUEST")["first_power_profile_disposition"] == "ACCEPT AS NO-OP / ZERO OUTPUT", "STOP is not a no-op")
    need(all(r["state"] == "OPEN - NOT EXECUTED" for r in holds), "hold falsely closed")
    for key in ["stm32_target_binary_built", "target_hil_executed", "firmware_approved", "functional_safety_credit", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"authority/evidence overclaim: {key}")
    need(status["host_compiled"] and status["host_vector_result"] == "PASS" and status["two_clean_host_builds_byte_identical"], "host compiled evidence missing")
    need(status["torque_enable_mask_constant"] == "0x00000000" and status["bus_tx_enable_mask_constant"] == "0x0000", "constant no-motion masks drift")
    need(all(r["sha256"] == sha(ROOT / r["path"]) for r in sources), "source binding drift")
    need((OUT / "firmware-package-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    for relative in ["include/hr30_motion.h", "src/hr30_motion.c", "tests/hr30_motion_vector_runner.c", "platform/stm32h743/hr30_stm32h743_io.h", "output/host-p0.1/build-evidence.json", "output/host-p0.1/hr30_motion_vector_runner.exe"]:
        need((OUT / relative).read_bytes() == (SOURCE / relative).read_bytes(), f"canonical firmware source drift: {relative}")
    evidence_path = OUT / "output/host-p0.1/build-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    binary = OUT / "output/host-p0.1" / evidence["binary"]["path"]
    log = OUT / "output/host-p0.1" / evidence["execution_log"]["path"]
    need(binary.stat().st_size == evidence["binary"]["bytes"] and sha(binary) == evidence["binary"]["sha256"], "host binary hash drift")
    need(log.stat().st_size == evidence["execution_log"]["bytes"] and sha(log) == evidence["execution_log"]["sha256"], "host log hash drift")
    for path_text, digest in evidence["source_sha256"].items():
        need(sha(ROOT / path_text) == digest, f"compiled source hash drift: {path_text}")
    completed = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True, check=False)
    need(completed.returncode == 0 and "PASS: HR-30 FIRST_POWER_NO_MOTION" in completed.stdout, "committed compiled runner failed")
    source = (OUT / "src/hr30_motion.c").read_text(encoding="utf-8")
    need("torque_enable_mask = UINT32_C(0)" in source and "bus_tx_enable_mask = UINT16_C(0)" in source, "C no-motion assignment missing")
    need("request->kind != HR30_ACTION_STOP_REQUEST" in source and "action_ready = false" in source, "C action gate drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["hr30_no_motion_firmware_present"] and root_status["hr30_no_motion_firmware_axis_count"] == 25 and root_status["hr30_no_motion_firmware_bus_count"] == 8, "root status integration missing")
    need(root_status["hr30_no_motion_target_hil_executed"] is False and root_status["hr30_no_motion_firmware_approved"] is False, "root firmware overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "The controller now boots with nowhere to move" in page, "firmware guide content/legibility drift")
    need("HR30-NO-MOTION-FW-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root page integration missing")
    print("PASS: HR-30 no-motion firmware binds 25 axes/8 buses, compiled host vectors pass, and all target/HIL/safety/authority gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
