"""Fail-closed checks for the HR-30 no-actuator STM32 bring-up package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "firmware" / "stm32-target-bringup-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "firmware" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_stm32_bringup_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "bring-up source/release missing")
    sources = rows(OUT / "primary-source-register.csv")
    bindings = rows(OUT / "source-binding.csv")
    contacts = rows(OUT / "debug-path-contact-map.csv")
    bom = rows(OUT / "debug-adapter-bom.csv")
    freeze = rows(OUT / "configuration-freeze.csv")
    gates = rows(OUT / "bringup-gate-register.csv")
    commands = rows(OUT / "command-plan.csv")
    measurements = rows(OUT / "measurement-plan.csv")
    faults = rows(OUT / "fault-injection-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "bringup-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 5 and len({r["source_id"] for r in sources}) == 5, "five primary sources required")
    need(all(r["url"].startswith("https://") and r["accessed"] == "2026-08-16" for r in sources), "source URL/access date drift")
    need(len(bindings) == 10 and all(r["sha256"] == sha(ROOT / r["path"]) and int(r["bytes"]) == (ROOT / r["path"]).stat().st_size for r in bindings), "ten source bindings required and must hash-match")
    need(len(contacts) == 7 and len({r["map_id"] for r in contacts}) == 7, "seven contact dispositions required")
    mapped = [r for r in contacts if r["target_connector"] == "JDBG1"]
    need(len(mapped) == 7 and {r["target_contact"] for r in mapped} == {"1", "2", "3", "4", "5"}, "JDBG1 mapping incomplete")
    need(sum(r["target_contact"] == "1" for r in mapped) == 3, "all three STDC14 grounds must map to JDBG1 ground")
    tvcc = next(r for r in contacts if r["signal"] == "TVCC")
    need(tvcc["probe_contact"] == "3" and tvcc["target_contact"] == "2" and "SENSE ONLY" in tvcc["wiring_rule"], "TVCC sense-only mapping drift")
    ground_detect = next(r for r in contacts if r["signal"] == "GNDDETECT")
    need(ground_detect["target_connector"] == "JDBG1" and ground_detect["target_contact"] == "1" and ground_detect["target_net"] == "CTRL_GND" and "TARGET SIGNAL GROUND" in ground_detect["wiring_rule"], "GNDDETECT mapping drift")

    need(len(bom) == 9 and sum(r["selection_state"] == "SELECTION REQUIRED" for r in bom) == 2, "adapter BOM coverage drift")
    need(all(r["procurement_released"] == "NO" for r in bom), "procurement falsely released")
    need(any(r["candidate_order_code"] == "STLINK-V3MINIE" for r in bom), "probe missing")
    need(any(r["candidate_order_code"] == "FTSH-107-01-L-DV-K-A" for r in bom), "STDC14 header missing")
    need(any(r["candidate_order_code"] == "BM05B-GHS-TBT" for r in bom), "JST header missing")
    need(any(r["item_id"] == "BR-P08" and r["selection_state"] == "PROJECT NATIVE CANDIDATE - PHYSICAL VALIDATION OPEN" and "hr30-swd-adapter-p0.1.kicad_pcb" in r["candidate_order_code"] for r in bom), "native adapter PCB candidate missing")

    firmware = json.loads((WHOLE / "firmware/hr30-motion-controller-p0.1/firmware-status.json").read_text(encoding="utf-8"))
    frozen = {r["parameter"]: r["value"] for r in freeze}
    need(len(freeze) == 8, "configuration freeze coverage drift")
    need(frozen["ELF SHA-256"] == firmware["stm32_target_elf_sha256"], "ELF hash freeze drift")
    need(frozen["BIN SHA-256"] == firmware["stm32_target_bin_sha256"], "BIN hash freeze drift")
    need(frozen["configuration binding SHA-256"] == firmware["stm32_target_configuration_binding_sha256"], "configuration hash freeze drift")
    need(frozen["configuration word"] == "0x6764f016", "configuration word drift")

    need(len(gates) == 10 and len({r["gate_id"] for r in gates}) == 10, "ten bring-up gates required")
    need(len(commands) == 5 and len(measurements) == 12 and len(faults) == 6 and len(holds) == 11, "traveler coverage drift")
    need(all(r["execution_state"] == "NOT EXECUTED" for r in contacts + bom + freeze + gates + commands + measurements + faults + holds), "physical activity falsely executed")
    need(all(r["pass_fail"] == "NOT EXECUTED" and r["completion_record"] == "NONE" for r in gates), "gate overclaim")
    need(all(r["measured_value"] == "NONE" and r["pass_fail"] == "NOT EXECUTED" for r in measurements), "measurement overclaim")
    need(all(r["measured_response"] == "NONE" and r["pass_fail"] == "NOT EXECUTED" for r in faults), "fault-injection overclaim")
    need(all(r["return_code"] == "NONE" and r["evidence_path"] == "NONE" for r in commands), "command execution overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold closure overclaim")
    need("-d <FROZEN_ELF_ABSOLUTE_PATH> -v" in next(r["command_template"] for r in commands if r["command_id"] == "BR-CMD04"), "download/verify template drift")
    need(all("option" not in r["command_template"].lower() and "erase" not in r["command_template"].lower() for r in commands), "destructive programmer option introduced")

    false_keys = [
        "stm32_target_binary_flashed", "adapter_cable_built", "logic_supply_selected",
        "target_hil_executed", "physical_torque_disabled_verified", "functional_safety_credit",
        "connection_authority", "powered_test_authority", "motion_authority", "energization_authority",
    ]
    need(status["stm32_target_binary_built"] is True, "built target evidence lost")
    need(status["adapter_pcb_designed"] is True and status["adapter_cable_design_present"] is True, "adapter design evidence lost")
    need(status["adapter_pcb_erc_errors"] == status["adapter_pcb_erc_warnings"] == status["adapter_pcb_drc_violations"] == 0, "adapter KiCad validation drift")
    need(all(status[key] is False for key in false_keys), "fail-closed status violated")
    need(status["physical_gate_executed_count"] == status["measurement_executed_count"] == status["fault_injection_executed_count"] == 0, "execution count overclaim")
    need((OUT / "stm32-target-bringup-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")

    terminals = {(r["reference"], r["pad"]): r["net"] for r in rows(WHOLE / "electrical/motion-controller-p0.1/terminal-register.csv")}
    expected = {("JDBG1", "1"): "CTRL_GND", ("JDBG1", "2"): "CTRL_3V3", ("JDBG1", "3"): "SWDIO", ("JDBG1", "4"): "SWCLK", ("JDBG1", "5"): "MCU_NRST"}
    need(all(terminals.get(key) == net for key, net in expected.items()), "authoritative JDBG1 terminal map drift")

    manifest = rows(OUT / "file-manifest.csv")
    expected_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected_files, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["stm32_target_bringup_package_present"] is True and root_status["stm32_target_bringup_gate_count"] == 10, "root status integration missing")
    need(root_status["stm32_target_bringup_flash_executed"] is False and root_status["energization_authority"] is False, "root authority overclaim")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "Flash the brain without connecting the muscles" in page, "web guide/legibility drift")
    need("native adapter guide" in page and "designed but not fabricated" in page and "cable is not built" in page, "designed-but-unbuilt boundary missing")
    need("HR30-STM32-BRINGUP-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    need("HR30-STM32-BRINGUP-P01-README-START" in (WHOLE / "README.md").read_text(encoding="utf-8"), "root README integration missing")
    print("PASS: HR-30 STM32 bring-up binds seven STDC14 contacts through the native unbuilt adapter, ten open gates, twelve unexecuted measurements, zero flashes/HIL, and no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
