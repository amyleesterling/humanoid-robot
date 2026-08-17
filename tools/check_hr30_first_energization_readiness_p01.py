"""Fail-closed checks for the HR-30 first-energization readiness package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-readiness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_first_energization_readiness_p01.py"


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
    gates, states = rows(OUT / "energization-gate-register.csv"), rows(OUT / "power-state-ladder.csv")
    traveler, faults = rows(OUT / "pre-energization-inspection-traveler.csv"), rows(OUT / "fault-injection-register.csv")
    measurements, signoffs = rows(OUT / "measurement-record.csv"), rows(OUT / "qualified-signoff-register.csv")
    holds, sources = rows(OUT / "open-holds.csv"), rows(OUT / "source-binding.csv")
    status = json.loads((OUT / "readiness-status.json").read_text(encoding="utf-8"))
    need(len(gates) == 12 and len({r["gate_id"] for r in gates}) == 12, "12 unique gates required")
    need(len(states) == 8 and len({r["state_id"] for r in states}) == 8, "8 unique power states required")
    need(len(traveler) == 26 and len(faults) == 12 and len(measurements) == 10, "traveler/fault/measurement coverage drift")
    need(len(signoffs) == 5 and len(holds) == 10 and len(sources) == 23, "signoff/hold/source coverage drift")
    need(all(r["state"] == "OPEN - NOT EXECUTED" for r in gates + states + traveler + faults + measurements + signoffs + holds), "physical work falsely marked executed")
    need(all(r["motion_permitted"] == "NO" for r in states), "motion permitted in energization ladder")
    need(all(r["pass_fail"] == "NOT EXECUTED" and r["measured_response"] == "NONE" for r in faults), "fault test overclaim")
    need(all(r["decision"] == "NOT SIGNED" and r["person"] == "UNASSIGNED" for r in signoffs), "signoff overclaim")
    need(all(r["measured_value"] == "NONE" and "SELECTION REQUIRED" in r["acceptance_limit"] for r in measurements), "measurement limit/result invented")
    need(all(r["sha256"] == sha(ROOT / r["path"]) for r in sources), "source-binding drift")
    for key in ["first_energization_ready", "motion_in_scope", "configuration_frozen", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["physical_gate_executed_count"] == status["fault_injection_executed_count"] == status["qualified_signoff_count"] == 0, "execution count overclaim")
    need(status["host_no_motion_firmware_evidence_present"] is True and status["stm32_target_binary_built"] is True and status["stm32_target_binary_flashed"] is False and status["target_no_motion_firmware_approved"] is False, "firmware evidence/approval boundary drift")
    need(status["stm32_target_bringup_plan_present"] is True and status["stm32_target_bringup_flash_executed"] is False, "bring-up evidence boundary drift")
    need(status["actuator_cable_coupon_plan_present"] is True and status["actuator_cable_coupon_built_count"] == 0 and status["actuator_cable_final_cut_length_count"] == 0, "cable coupon evidence boundary drift")
    need(any(r["hold_id"] == "FER-H04" and "zero production cut lengths" in r["unresolved_item"] for r in holds), "cable coupon hold not propagated")
    need(any(r["hold_id"] == "FER-H01" and "zero parts have been printed or inspected" in r["unresolved_item"] for r in holds), "full-scale fit-check physical boundary not propagated")
    need(any(r["hold_id"] == "FER-H05" and "whole-body SRS" in r["unresolved_item"] and "achieved PL/PFHd" in r["unresolved_item"] for r in holds), "SRS advancement/validation hold not propagated")
    need(any(r["hold_id"] == "FER-H06" and "complete stopping-time equation" in r["unresolved_item"] and "numerical allocation" in r["unresolved_item"] for r in holds), "stopping model/result boundary not propagated")
    fit_source = [r for r in sources if r["path"].endswith("full-scale-fit-check-p0.1/fit-check-status.json")]
    need(len(fit_source) == 1, "full-scale fit-check source binding missing")
    srs_source = [r for r in sources if r["path"].endswith("safety-requirements-p0.1/srs-status.json")]
    need(len(srs_source) == 1, "whole-body SRS source binding missing")
    need((OUT / "first-energization-readiness-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["first_energization_gate_count"] == 12 and root_status["first_energization_power_state_count"] == 8, "root status integration missing")
    need(root_status["first_energization_ready"] is False and root_status["energization_authority"] is False, "root authority overclaim")
    need(status["whole_body_srs_candidate_present"] is True and status["candidate_plr_allocation_present"] is True and status["candidate_plr_approved"] is False, "SRS evidence/approval boundary drift")
    need(status["stopping_time_model_present"] is True and status["stopping_time_measured"] is False and status["stopping_distance_allocated"] is False and status["functional_safety_validated"] is False, "stopping/safety boundary drift")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "A controlled route to first power" in page, "guide content/legibility drift")
    need("HR30-FIRST-ENERGIZATION-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    print("PASS: HR-30 first-energization path has 12 open gates, 8 unauthorized states, 0 executions, 0 signoffs, and no motion/energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
