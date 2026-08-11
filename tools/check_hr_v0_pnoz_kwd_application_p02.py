#!/usr/bin/env python3
"""Validate the R233 P1.20 PNOZ/KWD application dossier."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P120 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"
SAFETY = ROOT / "safety" / "hr-v0-pnoz-kwd-application-p0.2"
RELEASE = ROOT / "release" / "hr-v0" / "pnoz-kwd-application-p0.2"
DOC = ROOT / "docs" / "hr-v0-pnoz-kwd-application-p0.2.md"
REQUEST = ROOT / "docs" / "reviews" / "2026-08-11-r233-independent-review-request.md"
VALIDATION = ROOT / "docs" / "reviews" / "2026-08-11-r233-validation-record.md"
SUPPLEMENT = ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r233.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    manual = ROOT / "electrical/vendor/pilz/pnoz-s4-750104-r116/PNOZ_s4_21396-EN-23.pdf"
    need(hashlib.sha256(manual.read_bytes()).hexdigest().upper() == "4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4", "controlled Pilz manual hash drifted")
    schedule = {(r["sheet"], r["reference"], r["terminal"]): r for r in rows(P120 / "connector-schedule.csv")}
    expected_path = {
        ("02_estop_eligibility.kicad_sch", "SR1", "13"): "SRA1_S11",
        ("02_estop_eligibility.kicad_sch", "SR1", "14"): "SR1_OUT1_TO_KWD1",
        ("02_estop_eligibility.kicad_sch", "SR1", "23"): "SRA1_S21",
        ("02_estop_eligibility.kicad_sch", "SR1", "24"): "SR1_OUT2_TO_KWD2",
        ("03_arm_watchdog_eligibility.kicad_sch", "KWD1", "11"): "SR1_OUT1_TO_KWD1",
        ("03_arm_watchdog_eligibility.kicad_sch", "KWD1", "14"): "SRA1_S12",
        ("03_arm_watchdog_eligibility.kicad_sch", "KWD2", "11"): "SR1_OUT2_TO_KWD2",
        ("03_arm_watchdog_eligibility.kicad_sch", "KWD2", "14"): "SRA1_S22",
        ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", "S11"): "SRA1_S11",
        ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", "S12"): "SRA1_S12",
        ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", "S21"): "SRA1_S21",
        ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", "S22"): "SRA1_S22",
        ("03_arm_watchdog_eligibility.kicad_sch", "S2", "TBD-A1"): "SRA1_S12",
        ("03_arm_watchdog_eligibility.kicad_sch", "S2", "TBD-A2"): "ARM_AFTER_S2",
        ("04_contactor_edm.kicad_sch", "K1", "21"): "ARM_AFTER_S2",
        ("04_contactor_edm.kicad_sch", "K1", "22"): "EDM_K1_OUT",
        ("04_contactor_edm.kicad_sch", "K2", "21"): "EDM_K1_OUT",
        ("04_contactor_edm.kicad_sch", "K2", "22"): "SRA1_START_RETURN",
        ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", "S34"): "SRA1_START_RETURN",
    }
    for key, net in expected_path.items():
        need(key in schedule and schedule[key]["net"] == net, f"P1.20 path drifted: {key}")
    for directory in (SAFETY, RELEASE):
        source = rows(directory / "source-register.csv")
        need(len(source) == 2 and {r["manufacturer"] for r in source} == {"Pilz", "Phoenix Contact"}, f"{directory}: source register")
        need(source[0]["sha256"] == "4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4", f"{directory}: manual binding")
        path = rows(directory / "terminal-path-conformance.csv")
        need(len(path) == 31 and all(r["safety_credit"] == "NONE" for r in path), f"{directory}: terminal path")
        for row in path:
            key = (row["sheet"], row["reference"], row["terminal"])
            need(key in schedule and schedule[key]["net"] == row["net"] and schedule[key]["pin_name"] == row["pin_name"], f"{directory}: source parity {key}")
        screens = {r["screen_id"]: r for r in rows(directory / "electrical-compatibility.csv")}
        need(len(screens) == 12, f"{directory}: compatibility count")
        need(screens["APP-005"]["value"] == "4.8" and screens["APP-006"]["value"] == "5.0" and screens["APP-008"]["value"] == "75", f"{directory}: derived margins")
        need(screens["APP-011"]["disposition"] == "NOT AN ACCEPTANCE BOUND", f"{directory}: timing boundary")
        fault = rows(directory / "fault-behavior.csv")
        need(len(fault) == 10 and sum(r["disposition"] == "HAZARDOUS / OPEN" for r in fault) == 4, f"{directory}: fault boundary")
        need(len(rows(directory / "qualification-questions.csv")) == 10, f"{directory}: qualification questions")
        holds = rows(directory / "open-holds.csv")
        need(len(holds) == 9 and all(r["state"] == "OPEN" for r in holds), f"{directory}: open holds")
        finding = rows(directory / "b005-disposition.csv")
        need(len(finding) == 1 and finding[0]["current_disposition"] == "PARTIALLY_ADDRESSED_OPEN", f"{directory}: B005 disposition")
        need(finding[0]["qualified_closure"] == "NO" and finding[0]["safety_credit"] == "NONE" and finding[0]["work_authority"] == "NO", f"{directory}: B005 boundary")
        status = json.loads((directory / "status.json").read_text(encoding="utf-8"))
        need(status["candidate"] == "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE" and not status["p120_accepted"], f"{directory}: candidate boundary")
        need(status["safety_credit"] == "NONE" and not status["work_authority"], f"{directory}: authority")
        need(all(r["warning"] == WARNING for name in ("source-register.csv", "terminal-path-conformance.csv", "electrical-compatibility.csv", "fault-behavior.csv", "qualification-questions.csv", "open-holds.csv", "b005-disposition.csv") for r in rows(directory / name)), f"{directory}: warning coverage")
    manifest = {r["file"]: r for r in rows(RELEASE / "file-manifest.csv")}
    actual = {p.name: p for p in RELEASE.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "R233 manifest membership")
    for name, path in actual.items():
        data = path.read_bytes()
        need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest() and manifest[name]["size_bytes"] == str(len(data)), f"R233 manifest drift: {name}")
    page = (RELEASE / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "4.8×", "5.0×", "75×", "PARTIALLY ADDRESSED / OPEN", "zero safety credit"):
        need(token in page, f"interactive guide missing {token}")
    for path in (DOC, REQUEST, VALIDATION):
        text = path.read_text(encoding="utf-8")
        need(WARNING in text and "R233" in text and "P1.20" in text, f"{path}: boundary missing")
    validation = VALIDATION.read_text(encoding="utf-8")
    for token in ("176 / 176 PASS", "18 / 18 PASS", "67 / 67 PASS", "11 / 11 PASS", "visual desktop/mobile browser QA is not executed"):
        need(token in validation, f"validation record missing {token}")
    supplement = rows(SUPPLEMENT)
    need({r["gate_id"] for r in supplement} == {"EG-002", "EG-004", "EG-012", "EG-020", "EG-021", "EG-022"}, "R233 gate set")
    need(all(r["status"] == "REMAINS PARTIAL" and r["warning"] == WARNING for r in supplement), "R233 gate boundary")
    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    safety = next(item for item in candidate["current_products"] if item["domain"] == "functional_safety")
    need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "current electrical product changed")
    need(electrical["p120_pnoz_kwd_application_dossier"] == "HR-V0-PNOZ-KWD-APP-P0.2", "electrical R233 binding")
    need(safety["p120_pnoz_kwd_application_dossier"] == "HR-V0-PNOZ-KWD-APP-P0.2", "safety R233 binding")
    need("zero_safety_credit" in safety["release_state"] and "qualified_review_open" in safety["release_state"], "safety boundary weakened")
    print("HR-V0 PNOZ/KWD application check passed: 31 terminals, 12 screens, 10 faults, 9 open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
