#!/usr/bin/env python3
"""Validate the R246 P1.21 static voltage-budget and P0.10 configuration packages."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/analysis/hr-v0-p121-static-voltage-budget-p0.1"
REL = ROOT / "release/hr-v0/p121-static-voltage-budget-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.10"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.10"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path, fail) -> None:
    manifest = rows(directory / "file-manifest.csv")
    actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    fail({r["path"] for r in manifest} != actual, f"manifest membership: {directory}")
    for row in manifest:
        path = directory / row["path"]
        fail(not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"], f"manifest hash: {path}")


def main() -> int:
    errors: list[str] = []
    fail = lambda condition, message: errors.append(message) if condition else None
    common = {"README.md","source-register.csv","loop-topology-register.csv","manufacturer-operating-envelope.csv","series-element-register.csv","static-headroom-screen.csv","transient-case-register.csv","missing-input-register.csv","manufacturer-question-addendum.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","file-manifest.csv"}
    fail(not ENG.is_dir() or {p.name for p in ENG.iterdir() if p.is_file()} != common, "engineering membership")
    fail(not REL.is_dir() or {p.name for p in REL.iterdir() if p.is_file()} != common | {"index.html"}, "release membership")
    check_manifest(ENG, fail); check_manifest(REL, fail)
    for name in common - {"file-manifest.csv"}:
        fail((ENG / name).read_bytes() != (REL / name).read_bytes(), f"engineering/release mismatch: {name}")
    status = json.loads((REL / "package-status.json").read_text(encoding="utf-8"))
    expected = {"identifier":"HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1","round":"R246","status":"PARTIAL / NOT ACCEPTED","loop_records":8,"manufacturer_sources":8,"series_elements":18,"static_screens":6,"transient_cases":8,"missing_inputs":18,"manufacturer_questions":10,"open_holds":10,"warning":WARNING}
    for key, value in expected.items(): fail(status.get(key) != value, f"status {key}")
    for key in ("accepted_installed_voltage_budget","p121_accepted","physical_evidence_exists","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        fail(status.get(key) is not False, f"{key} must be false")
    fail(status.get("p115_current") is not True, "P1.15 must stay current")
    fail("GlobTek" not in status.get("source_boundary", "") or "Mean Well" not in status.get("source_boundary", "") or "excluded" not in status.get("source_boundary", "").lower(), "source boundary")

    sources = {r["source_id"]: r for r in rows(REL / "source-register.csv")}
    fail(len(sources) != 8, "eight sources")
    for token in ("Rev B","21396-EN-23","2967060","SLRS066D","SQD-LC1D25BD","2024-02-07","Rev C2","GST280A"):
        fail(token not in " ".join(" ".join(r.values()) for r in sources.values()), f"source token: {token}")
    fail(sources.get("SRC-008", {}).get("status") != "EXCLUDED SOURCE BOUNDARY", "Mean Well exclusion")

    loops = rows(REL / "loop-topology-register.csv")
    fail(len(loops) != 8 or {r["loop_id"] for r in loops} != {f"LOOP-{n:03d}" for n in range(1,9)}, "loop set")
    loop_text = " ".join(" ".join(r.values()) for r in loops)
    for token in ("J24:1","F24:IN/OUT","SR1:A1","SR1:A2","SRA1:A1","KWD1:11-14","KWD2:11-14","JWP1:3","JWP1:4","XD0:07"):
        fail(token not in loop_text, f"loop token: {token}")
    fail("GST280" in loop_text, "actuator source may not enter control loops")

    connector = rows(P121 / "connector-schedule.csv")
    actual = {(r["reference"], r["terminal"], r["net"]) for r in connector}
    required = {("J24","1","SAFETY_24V_RAW"),("J24","3","SAFETY_0V"),("SR1","A1","SAFETY_24V"),("SR1","A2","SAFETY_0V"),("SRA1","A1","SRA1_A1_WD_GATED"),("SRA1","A2","SAFETY_0V"),("KWD1","A1","SAFETY_24V"),("KWD1","A2","WD1_COIL_N"),("KWD2","A1","SAFETY_24V"),("KWD2","A2","WD2_COIL_N"),("JWP1","1","SAFETY_24V"),("JWP1","2","SAFETY_0V"),("JWP1","3","WD1_COIL_N"),("JWP1","4","WD2_COIL_N")}
    fail(not required.issubset(actual), f"P1.21 terminal/net mismatch: {sorted(required-actual)}")

    env = {r["load_id"]: r for r in rows(REL / "manufacturer-operating-envelope.csv")}
    expected_env = {"ENV-001":(20.4,26.4,2.4,1.2),"ENV-002":(20.2,33.6,2.6,8.4),"ENV-003":(16.8,30.0,6.0,4.8),"ENV-004":(6.5,36.0,16.3,10.8)}
    fail(set(env) != set(expected_env), "envelope set")
    for key, values in expected_env.items():
        row = env[key]
        for field, value in zip(("published_min_V","published_max_V","raw_low_headroom_V","raw_high_headroom_V"), values):
            fail(not math.isclose(float(row[field]), value, abs_tol=1e-9), f"{key} {field}")
        fail(row["status"] != "PARTIAL", f"{key} status")

    series = rows(REL / "series-element-register.csv")
    fail(len(series) != 18, "eighteen series elements")
    fail(sum(1 for r in series if r["disposition"] == "SELECTION REQUIRED") < 10, "series selection boundary")
    fail(any(r["usable_bound"] == "YES" and r["element_id"] != "SER-001" for r in series), "only source connector may be bounded")
    screens = {r["screen_id"]: r for r in rows(REL / "static-headroom-screen.csv")}
    expected_drop = {"SCR-001":.002060,"SCR-002":.002262,"SCR-003":.000338,"SCR-004":.000331}
    fail(set(screens) != {f"SCR-{n:03d}" for n in range(1,7)}, "six screen records")
    for key, value in expected_drop.items():
        fail(not math.isclose(float(screens[key]["known_nominal_forward_drop_V"]), value, abs_tol=5e-7), f"nominal drop {key}")
    fail(any(r["accepted_installed_margin_V"] != "NOT CALCULABLE" for r in screens.values()), "installed margin must remain uncalculated")
    fail(any(not r["result"].startswith("PARTIAL") for r in screens.values()), "screen results partial")

    fail(len(rows(REL / "transient-case-register.csv")) != 8 or any(r["result"] != "NOT CALCULABLE" for r in rows(REL / "transient-case-register.csv")), "transients remain uncalculated")
    fail(len(rows(REL / "missing-input-register.csv")) != 18, "eighteen missing inputs")
    fail(len(rows(REL / "manufacturer-question-addendum.csv")) != 10 or any(r["state"] != "UNSENT" for r in rows(REL / "manufacturer-question-addendum.csv")), "questions unsent")
    fail(len(rows(REL / "open-holds.csv")) != 10 or any(r["state"] != "OPEN" for r in rows(REL / "open-holds.csv")), "ten holds open")
    fail(len(rows(REL / "acceptance-matrix.csv")) != 7 or any(r["execution_state"] != "NOT EXECUTED" or r["result"] != "OPEN" for r in rows(REL / "acceptance-matrix.csv")), "acceptance open")
    page = (REL / "index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","PARTIAL / NOT ACCEPTED","8","18"):
        fail(token not in page, f"web token: {token}")

    cfg_common = {"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    fail({p.name for p in CFG.iterdir() if p.is_file()} != cfg_common, "configuration membership")
    fail({p.name for p in CFG_REL.iterdir() if p.is_file()} != cfg_common | {"index.html"}, "configuration release membership")
    check_manifest(CFG, fail); check_manifest(CFG_REL, fail)
    cfg = json.loads((CFG_REL / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {"identifier":"HR-V0-CONFIG-REC-P0.10","round":"R246","system_bom_groups":98,"current_records":30,"supersession_records":17,"bom_integration_records":18,"gate_records":11,"open_holds":41,"acceptance_rows":57,"p121_static_voltage_budget":"HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1"}.items():
        fail(cfg.get(key) != value, f"config {key}")
    fail(cfg.get("current_core_electrical_identifier") != "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 current config")
    fail(cfg.get("unaccepted_panel_topology_candidate") != "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "P1.21 unaccepted config")
    current = rows(CFG_REL / "current-configuration-map.csv")
    fail(len(current) != 30 or current[-1]["identifier"] != "HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1", "current config map")
    hashes = rows(CFG_REL / "source-hash-register.csv")
    fail(len(hashes) != 30, "thirty source hashes")
    for row in hashes:
        source = ROOT / row["source_path"]
        fail(not source.is_file() or digest(source) != row["sha256"], f"source hash: {row['source_path']}")
    fail(len(rows(ROOT / "bom/bom.csv")) != 98, "98 BOM groups unchanged")

    if errors:
        print("HR-V0 R246 P1.21 static voltage budget: FAIL")
        for error in errors: print("-", error)
        return 1
    print("HR-V0 R246 P1.21 static voltage budget: PASS")
    print("8 loops; 6 raw-headroom screens; 18 missing inputs; installed margin remains NOT CALCULABLE")
    print("P1.15 current; P1.21 partial/unaccepted; no work, safety or energization authority")
    return 0


if __name__ == "__main__": raise SystemExit(main())
