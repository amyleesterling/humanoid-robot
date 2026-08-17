"""Fail-closed checks for the HR-30 whole-body SRS candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "safety-requirements-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_safety_requirements_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release SRS package missing")
    sources = rows(OUT / "source-register.csv")
    lifecycle = rows(OUT / "lifecycle-mode-register.csv")
    hazards = rows(OUT / "hazard-register.csv")
    functions = rows(OUT / "safety-function-register.csv")
    plr = rows(OUT / "plr-calculation-input-register.csv")
    ccf = rows(OUT / "common-cause-control-register.csv")
    zero_motion = rows(OUT / "zero-motion-invariant-register.csv")
    timings = rows(OUT / "stopping-time-budget.csv")
    stopping = rows(OUT / "stopping-distance-register.csv")
    validations = rows(OUT / "validation-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "srs-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 23 and sum(r["source_type"] == "OFFICIAL EXTERNAL" for r in sources) == 11, "source coverage drift")
    need(len(lifecycle) == 14 and len({r["mode_id"] for r in lifecycle}) == 14, "lifecycle coverage drift")
    need(len(hazards) == 24 and len({r["hazard_id"] for r in hazards}) == 24, "24 unique hazards required")
    need(all(r["residual_risk_disposition"].startswith("OPEN") for r in hazards), "hazard risk falsely accepted")
    need(all(r["validation_state"] == "NOT VALIDATED" for r in hazards), "hazard validation overclaim")
    need(any(r["hazard_id"] == "HZ-01" and r["candidate_required_pl"] == "d" for r in hazards), "unexpected-motion PLr candidate missing")
    need(any(r["hazard_id"] == "HZ-10" and "falls" in r["hazardous_event"] for r in hazards), "whole-body fall hazard missing")
    need(any(r["hazard_id"] == "HZ-21" and "conversational-agent" in r["hazardous_event"] for r in hazards), "AI boundary hazard missing")

    need(len(functions) == 12 and len({r["function_id"] for r in functions}) == 12, "12 unique function records required")
    need(sum(r["candidate_plr"] == "d" for r in functions) == 7, "candidate PLr d allocation drift")
    need(all(r["achieved_pl_claimed"] == "NO" for r in functions), "achieved PL overclaim")
    need(any(r["function_id"] == "SFR-02" and "reset cannot command motion" in r["restart_inhibition"] for r in functions), "reset/restart invariant missing")
    need(any(r["function_id"] == "SFR-07" and r["candidate_plr"] == "NOT ALLOCATED" and "NO SAFETY CREDIT" in r["implementation_state"] for r in functions), "watchdog safety-credit boundary drift")
    need(any(r["function_id"] == "SFR-11" and "MOTION PROHIBITED" in r["implementation_state"] for r in functions), "future speed/travel hold missing")

    need(len(plr) == 12 and {r["function_id"] for r in plr} == {r["function_id"] for r in functions}, "PL calculation input coverage drift")
    need(all(r["pfhd"] == r["achieved_pl"] == "NOT CALCULATED" and r["reviewer_disposition"] == "NOT REVIEWED" for r in plr), "PL calculation falsely completed")
    need(all(r["excluded_faults"] == "NONE ACCEPTED" for r in plr), "fault exclusion invented")
    need(len(ccf) == 10 and all(r["validation_state"] == "NOT VALIDATED" for r in ccf), "CCF coverage/validation drift")
    need(len(zero_motion) == 15 and all(r["physical_result"] == "NOT EXECUTED" for r in zero_motion), "zero-motion evidence overclaim")
    need(any(r["invariant_id"] == "ZMI-08" and "cannot create a motion request" in r["invariant"] for r in zero_motion), "manual-reset invariant missing")
    need(any(r["invariant_id"] == "ZMI-14" and "SELECTION REQUIRED" in r["acceptance_requirement"] for r in zero_motion), "physical motion threshold invented")

    need(len(timings) == 8 and {r["symbol"] for r in timings} == {"t_input", "t_logic", "t_output", "t_contactor", "t_bus", "t_torque", "t_mechanical", "T_total"}, "stopping-time model drift")
    need(all(r["allocated_max"] == "SELECTION REQUIRED" and r["measured_value"] == "NONE" for r in timings), "stopping time falsely allocated/measured")
    need(any(r["symbol"] == "T_total" and "t_input + t_logic + t_output + t_contactor + t_bus + t_torque + t_mechanical" in r["interval"] for r in timings), "total stop-time equation drift")
    axes = rows(WHOLE / "actuator-transmission-allocation.csv")
    expected_axes = {r.get("axis_id") or r.get("joint_id") or next(iter(r.values())) for r in axes}
    need(len(stopping) == 25 and {r["axis_id"] for r in stopping} == expected_axes, "25-axis stopping-distance coverage drift")
    need(all(r["angular_overtravel_deg"] == r["endpoint_overtravel_mm"] == "NOT CALCULATED" and r["accepted_limit"] == "SELECTION REQUIRED BEFORE MOTION" for r in stopping), "stopping distance overclaim")

    need(len(validations) == 20 and all(r["result"] == "NOT EXECUTED" and r["reviewer"] == "UNASSIGNED" for r in validations), "validation execution overclaim")
    need({r["function_id"] for r in functions}.issubset({r["function_id"] for r in validations}), "not every function has a validation route")
    need(len(holds) == 12 and all(r["state"] == "OPEN" for r in holds), "SRS hold coverage drift")
    need(any(r["hold_id"] == "SRS-H10" and "child" in r["open_item"] for r in holds), "child/public scope hold missing")

    official = [r for r in sources if r["source_type"] == "OFFICIAL EXTERNAL"]
    local = [r for r in sources if r["source_type"] == "LOCAL CONFIGURATION"]
    need(all(r["path_or_url"].startswith("https://") and r["sha256"] == "REMOTE DOCUMENT - NOT VENDORED" and r["access_date"] == "2026-08-16" for r in official), "official-source record drift")
    need(all(r["sha256"] == sha(ROOT / r["path_or_url"]) for r in local), "local source hash drift")
    need(any(r["document"] == "ISO 13849-1:2023" and "does not prescribe" in r["use"] for r in official), "ISO 13849 PLr boundary missing")
    need(any(r["document"] == "ISO 13855:2024" and "age 14+" in r["use"] and "gravity falls" in r["use"] for r in official), "ISO 13855 scope boundary missing")

    for key in [
        "candidate_plr_approved", "achieved_performance_level_calculated", "stopping_time_measured",
        "stopping_distance_allocated", "functional_safety_validated", "qualified_review_complete",
        "connection_authority", "powered_test_authority", "motion_authority", "energization_authority",
    ]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["accepted_residual_risk_count"] == status["achieved_pl_claim_count"] == status["executed_validation_count"] == 0, "status evidence overclaim")
    need(status["candidate_plr_allocation_present"] is True and status["stopping_time_model_present"] is True, "candidate SRS advancement missing")

    need((OUT / "safety-requirements-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["whole_body_hazard_count"] == 24 and root_status["whole_body_safety_function_count"] == 12, "root status integration missing")
    need(root_status["candidate_plr_allocation_present"] is True and root_status["candidate_plr_approved"] is False and root_status["functional_safety_validated"] is False, "root safety boundary drift")
    need("HR30-SRS-P01-README-START" in (WHOLE / "README.md").read_text(encoding="utf-8"), "root README integration missing")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "Define the safe state before applying power" in page, "SRS guide content/legibility drift")
    need("HR30-SRS-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    svg = (OUT / "safety-architecture.svg").read_text(encoding="utf-8")
    need("font-size:16px" in svg and "NO VALIDATED PL" in svg, "SRS diagram legibility/warning drift")
    print("PASS: HR-30 SRS candidate has 24 open hazards, 12 function records, 8 unmeasured stop-time intervals, 25 uncalculated stopping-distance rows, 0 achieved PL claims, and no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
