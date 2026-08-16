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
    need(len(actions) == 10 and len(faults) == 6 and len(holds) == 11 and len(ios) == 10 and len(sources) == 17, "firmware register coverage drift")
    need(all(r["torque_command"] == "COMPILE-TIME DISABLED" and r["bus_transmit"] == "COMPILE-TIME DISABLED" for r in axes), "axis output path enabled")
    need(all(r["transmit_enable"] == "COMPILE-TIME DISABLED" for r in buses), "bus transmit path enabled")
    need(all(r["motion_possible"] == "NO" and r["torque_enable_mask"] == "0x00000000" and r["bus_tx_enable_mask"] == "0x0000" for r in actions), "action disposition permits motion")
    need(sum(r["first_power_profile_disposition"].startswith("ACCEPT") for r in actions) == 1, "only STOP may be accepted")
    need(next(r for r in actions if r["action"] == "STOP_REQUEST")["first_power_profile_disposition"] == "ACCEPT AS NO-OP / ZERO OUTPUT", "STOP is not a no-op")
    need(all(r["state"] == "OPEN - NOT EXECUTED" for r in holds), "hold falsely closed")
    for key in ["stm32_target_binary_flashed", "target_hil_executed", "oscilloscope_boot_state_verified", "physical_uart_write_path_audited", "physical_torque_disabled_verified", "firmware_approved", "functional_safety_credit", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"authority/evidence overclaim: {key}")
    need(status["host_compiled"] and status["host_vector_result"] == "PASS" and status["two_clean_host_builds_byte_identical"], "host compiled evidence missing")
    need(status["stm32_target_binary_built"] and status["stm32_target_build_reproducible"] and status["stm32_target_core_vectors_pass"] and status["stm32_target_mmio_vectors_pass"], "STM32 target build evidence missing")
    need(status["torque_enable_mask_constant"] == "0x00000000" and status["bus_tx_enable_mask_constant"] == "0x0000", "constant no-motion masks drift")
    need(all(r["sha256"] == sha(ROOT / r["path"]) for r in sources), "source binding drift")
    need((OUT / "firmware-package-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    for relative in [
        "include/hr30_motion.h", "src/hr30_motion.c", "tests/hr30_motion_vector_runner.c",
        "tests/hr30_stm32h743_mmio_runner.c", "platform/stm32h743/hr30_stm32h743_io.h",
        "platform/stm32h743/hr30_stm32h743_registers.h", "platform/stm32h743/hr30_stm32h743_target.h",
        "platform/stm32h743/hr30_stm32h743_target.c", "platform/stm32h743/startup_hr30_stm32h743.S",
        "platform/stm32h743/stm32h743zit6_hr30.ld", "target-toolchain-lock.json",
        "output/host-p0.1/build-evidence.json", "output/host-p0.1/hr30_motion_vector_runner.exe",
        "output/stm32h743-p0.1/build-evidence.json", "output/stm32h743-p0.1/hr30-motion-controller-stm32h743.elf",
        "output/stm32h743-p0.1/hr30-motion-controller-stm32h743.bin",
    ]:
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
    target_dir = OUT / "output/stm32h743-p0.1"
    target_evidence = json.loads((target_dir / "build-evidence.json").read_text(encoding="utf-8-sig"))
    need(target_evidence["configuration_binding_sha256"] == "6764f0163c02e7b52f6f76cfcbd5b90ea4c37cd292e459d9e99bc6981baed471", "target configuration binding drift")
    need(target_evidence["configuration_word"] == "0x6764f016" and target_evidence["vector_count"] == 166, "target configuration/vector metadata drift")
    need(target_evidence["two_clean_target_builds_byte_identical"] and target_evidence["core_compiled_vectors"] == "PASS" and target_evidence["mmio_compiled_vectors"] == "PASS", "target compiled evidence failed")
    need(all(target_evidence[k] is False for k in ["target_binary_flashed", "target_hil_executed", "oscilloscope_boot_state_verified", "physical_uart_write_path_audited", "functional_safety_credit", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]), "target evidence overclaims physical execution or authority")
    for artifact in target_evidence["artifacts"]:
        path = target_dir / artifact["path"]
        need(path.stat().st_size == artifact["bytes"] and sha(path) == artifact["sha256"] and artifact["builds_match"], f"target artifact drift: {artifact['path']}")
    for path_text, digest in target_evidence["source_sha256"].items():
        need(sha(ROOT / path_text) == digest, f"target compiled source hash drift: {path_text}")
    need(status["stm32_target_elf_sha256"] == target_evidence["artifacts"][0]["sha256"] and status["stm32_target_bin_sha256"] == target_evidence["artifacts"][1]["sha256"], "target status artifact hash drift")
    disassembly = (target_dir / "disassembly.txt").read_text(encoding="utf-8")
    inspection = (target_dir / "elf-inspection.txt").read_text(encoding="utf-8")
    need("cpsid i" in disassembly and "hr30_target_early_safe" in disassembly and "hr30_target_fault_hold" in disassembly, "target startup/fault-hold code absent")
    need(".isr_vector" in inspection and "000298" in inspection and "Reset_Handler" in inspection, "target vector table inspection drift")
    target_source = (OUT / "platform/stm32h743/hr30_stm32h743_target.c").read_text(encoding="utf-8")
    need("HR30_RCC_APB1_UART_MASK" in target_source and "HR30_RCC_APB2_UART_MASK" in target_source and "value & ~" in target_source, "target does not explicitly disable UART clocks")
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
    need(root_status["hr30_no_motion_stm32_target_built"] is True and root_status["hr30_no_motion_stm32_target_flashed"] is False, "root target build integration drift")
    need(root_status["hr30_no_motion_target_hil_executed"] is False and root_status["hr30_no_motion_firmware_approved"] is False, "root firmware overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "The controller target now exists" in page, "firmware guide content/legibility drift")
    need("HR30-NO-MOTION-FW-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root page integration missing")
    print("PASS: HR-30 no-motion firmware binds 25 axes/8 buses; reproducible host and unflashed STM32 target evidence passes; HIL/safety/authority gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
